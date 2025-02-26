import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, RegexpTokenizer
from nltk.stem.wordnet import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx
import pandas as pd
from community import community_louvain
import numpy as np
from gensim.models import Phrases
from gensim.corpora import Dictionary

class TextAnalyzer:
    def __init__(self, df, custom_stopwords=None):
        self.df = df
        # Initialize NLTK resources with error handling
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)

        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
            
        try:
            nltk.data.find('wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)

        # Initialize stopwords with fallback
        try:
            self.stop_words = set(stopwords.words('english'))
            
            # Add custom stopwords
            additional_stopwords = [
                'from', 'subject', 're', 'edu', 'use', 'not', 'would', 'say', 
                'could', '_', 'be', 'know', 'good', 'go', 'get', 'do', 'done', 
                'try', 'many', 'some', 'nice', 'thank', 'think', 'see', 'rather', 
                'easy', 'easily', 'lot', 'lack', 'make', 'want', 'seem', 'run', 
                'need', 'even', 'right', 'line', 'even', 'also', 'may', 'take', 'come',
                'odds', 'ratio', 'confidence', 'interval', 'mean', 'standard', 'deviation',
                'statistical', 'significance', 'significant', 'results', 'result', 'study',
                'studies', 'data', 'analysis', 'method', 'methods', 'model', 'models', 'variable',
                'cell', 'month', 'case', 'report', 'control', 'regression', 'cause', 'incidence', 'rate',
                'cross', 'sectional', 'cohort', 'prospective', 'retrospective', 'present', 'presented'
            ]
            self.stop_words.update(additional_stopwords)
            
            # Add any user-provided custom stopwords
            if custom_stopwords:
                self.stop_words.update(custom_stopwords)
                
        except Exception as e:
            print(f"Warning: Could not load stopwords, using minimal set: {str(e)}")
            self.stop_words = set(['and', 'or', 'the', 'a', 'an', 'in', 'on', 'at', 'of'])

        self.tokenizer = RegexpTokenizer(r'\w+')
        self.lemmatizer = WordNetLemmatizer()
        self.vectorizer = None
        self.lda_model = None
        self.dictionary = None
        self.corpus = None
        
    def extend_stopwords(self, new_stopwords):
        """
        Add additional words to the stopwords list
        
        Args:
            new_stopwords (list): List of words to add to stopwords
        """
        if isinstance(new_stopwords, (list, set, tuple)):
            self.stop_words.update(new_stopwords)
            return True
        return False

    def preprocess_text(self, text):
        """Basic preprocessing for simple text analysis"""
        if isinstance(text, str):
            tokens = self.tokenizer.tokenize(text.lower())
            tokens = [t for t in tokens if t.isalnum() and t not in self.stop_words]
            return ' '.join(tokens)
        return ''

    def advanced_preprocess_docs(self, texts):
        """Advanced preprocessing for topic modeling with lemmatization and n-grams"""
        # Convert texts to a list if it's a pandas Series
        if isinstance(texts, pd.Series):
            docs = texts.fillna('').tolist()
        else:
            docs = texts
            
        # Tokenize and lowercase
        tokenized_docs = []
        for doc in docs:
            if isinstance(doc, str):
                tokens = self.tokenizer.tokenize(doc.lower())
                # Remove stopwords
                tokens = [t for t in tokens if t not in self.stop_words]
                # Remove numbers but keep words with numbers
                tokens = [t for t in tokens if not t.isdigit()]
                # Remove short tokens
                tokens = [t for t in tokens if len(t) > 3]
                # Lemmatize
                tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
                tokenized_docs.append(tokens)
            else:
                tokenized_docs.append([])
                
        # Add bigrams and trigrams (for tokens appearing frequently)
        try:
            bigram = Phrases(tokenized_docs, min_count=5)
            trigram = Phrases(bigram[tokenized_docs])
            
            for idx in range(len(tokenized_docs)):
                for token in bigram[tokenized_docs[idx]]:
                    if '_' in token:
                        tokenized_docs[idx].append(token)
                for token in trigram[tokenized_docs[idx]]:
                    if '_' in token:
                        tokenized_docs[idx].append(token)
                        
            # Create gensim dictionary
            self.dictionary = Dictionary(tokenized_docs)
            # Filter extreme words
            self.dictionary.filter_extremes(no_below=5, no_above=0.2)
            
            # Create corpus
            self.corpus = [self.dictionary.doc2bow(doc) for doc in tokenized_docs]
            
            # For sklearn compatibility, convert back to strings
            processed_docs = [' '.join(doc) for doc in tokenized_docs]
            return processed_docs, tokenized_docs
            
        except Exception as e:
            print(f"Error in advanced preprocessing: {str(e)}")
            return [' '.join(doc) for doc in tokenized_docs], tokenized_docs

    def compute_coherence_score(self, topic_word_dist, vocabulary):
        """Compute topic coherence score."""
        coherence_scores = []
        for topic_dist in topic_word_dist:
            top_words_idx = topic_dist.argsort()[:-10:-1]
            top_words = [vocabulary[i] for i in top_words_idx]
            score = 0
            for i, word1 in enumerate(top_words):
                for word2 in top_words[i+1:]:
                    # Compute word co-occurrence
                    cooccurrence = sum(1 for text in self.df['processed_text'] 
                                    if word1 in text and word2 in text)
                    if cooccurrence > 0:
                        score += np.log(cooccurrence + 1)
            coherence_scores.append(score)
        return np.mean(coherence_scores)

    def extract_topics(self, n_topics=5, learning_method='online', max_iter=10, n_jobs=-1, use_advanced_preprocessing=True):
        """Extract topics with enhanced parameters and metrics using advanced preprocessing."""
        try:
            # Combine title and abstract
            texts = self.df['title'].fillna('') + ' ' + self.df['abstract'].fillna('')
            
            if use_advanced_preprocessing:
                # Use the advanced preprocessing pipeline
                processed_texts, tokenized_docs = self.advanced_preprocess_docs(texts)
                # Store processed text in DataFrame for coherence calculation
                self.df['processed_text'] = processed_texts
                
                # Use CountVectorizer but with our pre-processed vocabulary
                vocab = {word: idx for idx, word in enumerate(self.dictionary.token2id.keys())}
                self.vectorizer = CountVectorizer(
                    vocabulary=vocab,
                    max_df=0.95,
                    min_df=2
                )
            else:
                # Use the basic preprocessing
                processed_texts = texts.apply(self.preprocess_text)
                self.df['processed_text'] = processed_texts
                # Create document-term matrix with standard CountVectorizer
                self.vectorizer = CountVectorizer(
                    max_features=1000,
                    stop_words='english',
                    max_df=0.95,
                    min_df=2
                )
            
            # Create document-term matrix
            dtm = self.vectorizer.fit_transform(processed_texts)

            # Apply LDA with specified parameters
            self.lda_model = LatentDirichletAllocation(
                n_components=n_topics,
                random_state=42,
                learning_method=learning_method,
                max_iter=max_iter,
                n_jobs=n_jobs
            )
            doc_topics = self.lda_model.fit_transform(dtm)

            # Get feature names and prepare topics dictionary
            feature_names = self.vectorizer.get_feature_names_out()
            topics = {}
            topic_word_weights = []

            for topic_idx, topic in enumerate(self.lda_model.components_):
                top_words_idx = topic.argsort()[:-10:-1]
                top_words = [feature_names[i] for i in top_words_idx]
                top_weights = [topic[i] for i in top_words_idx]
                topics[f"Topic {topic_idx+1}"] = {
                    'words': top_words,
                    'weights': top_weights
                }
                topic_word_weights.append(topic)

            # Compute topic coherence
            coherence_score = self.compute_coherence_score(
                self.lda_model.components_,
                feature_names
            )

            # Compute topic diversity
            topic_diversity = len(set(
                word for topic in topics.values() 
                for word in topic['words']
            )) / (len(topics) * 10)  # 10 words per topic

            return {
                'topics': topics,
                'doc_topics': doc_topics,
                'coherence_score': coherence_score,
                'topic_diversity': topic_diversity,
                'perplexity': self.lda_model.perplexity(dtm),
                'dictionary': self.dictionary,
                'corpus': self.corpus
            }

        except Exception as e:
            print(f"Error in topic extraction: {str(e)}")
            return {
                'topics': {},
                'doc_topics': None,
                'coherence_score': 0,
                'topic_diversity': 0,
                'perplexity': float('inf'),
                'dictionary': None,
                'corpus': None
            }

    def get_topic_trends(self, doc_topics):
        """Analyze topic trends over time."""
        if doc_topics is None:
            return pd.DataFrame()

        # Create DataFrame with topic distributions and year
        topic_trends = pd.DataFrame(doc_topics)
        topic_trends.columns = [f"Topic {i+1}" for i in range(topic_trends.shape[1])]
        topic_trends['year'] = self.df['year']

        # Calculate yearly topic proportions
        yearly_trends = topic_trends.groupby('year').mean()

        return yearly_trends

    def create_coauthor_network(self, max_nodes=100):
        try:
            G = nx.Graph()

            # Create edges with weights
            collaborations = {}
            for _, row in self.df.iterrows():
                authors = row['author_list']
                if isinstance(authors, list):
                    for i in range(len(authors)):
                        for j in range(i+1, len(authors)):
                            pair = tuple(sorted([authors[i], authors[j]]))
                            collaborations[pair] = collaborations.get(pair, 0) + 1

            # Sort collaborations by weight and take top ones
            sorted_collabs = sorted(collaborations.items(), key=lambda x: x[1], reverse=True)

            # Get top authors based on collaboration frequency
            top_authors = set()
            for (author1, author2), _ in sorted_collabs:
                if len(top_authors) >= max_nodes:
                    break
                top_authors.add(author1)
                top_authors.add(author2)

            # Add weighted edges only for top authors
            for (author1, author2), weight in collaborations.items():
                if author1 in top_authors and author2 in top_authors:
                    G.add_edge(author1, author2, weight=weight)

            # Calculate node properties for the smaller network
            if len(G.nodes()) > 0:
                # Degree centrality
                centrality = nx.degree_centrality(G)
                nx.set_node_attributes(G, centrality, 'centrality')

                # Publication count
                author_pubs = self.df['author_list'].explode().value_counts()
                author_pubs = {author: count for author, count in author_pubs.items()
                             if author in top_authors}
                nx.set_node_attributes(G, author_pubs, 'publications')

                # Citation count (sum of citations for all papers)
                author_citations = {}
                for _, row in self.df.iterrows():
                    citations = row.get('citations', 0)
                    for author in row['author_list']:
                        if author in top_authors:
                            author_citations[author] = author_citations.get(author, 0) + citations
                nx.set_node_attributes(G, author_citations, 'citations')

                # Detect communities with error handling for scipy compatibility issues
                try:
                    communities = community_louvain.best_partition(G)
                    nx.set_node_attributes(G, communities, 'community')
                except ImportError as e:
                    print(f"Community detection error: {e}")
                    # Fallback: assign communities based on basic node clustering
                    # This is simpler but doesn't require the problematic import
                    from networkx.algorithms import community
                    communities = {node: i for i, com in enumerate(community.greedy_modularity_communities(G)) 
                                 for node in com}
                    nx.set_node_attributes(G, communities, 'community')

            return G
        except Exception as e:
            print(f"Error creating coauthor network: {str(e)}")
            return nx.Graph()

    def build_keyword_network(self, min_edge_weight=2):
        """Build a network of co-occurring keywords."""
        try:
            G = nx.Graph()
            keyword_pairs = {}

            # Process each row's keywords
            for keywords in self.df['author_keywords'].dropna():
                if isinstance(keywords, str):
                    # Split keywords and clean them
                    keyword_list = [kw.strip().lower() for kw in keywords.split(';')]
                    # Create pairs of keywords
                    for i, kw1 in enumerate(keyword_list):
                        for kw2 in keyword_list[i+1:]:
                            if kw1 and kw2:  # Ensure both keywords are non-empty
                                pair = tuple(sorted([kw1, kw2]))
                                keyword_pairs[pair] = keyword_pairs.get(pair, 0) + 1

            # Add edges with weights above threshold
            for (kw1, kw2), weight in keyword_pairs.items():
                if weight >= min_edge_weight:
                    G.add_edge(kw1, kw2, weight=weight)

            # Remove isolated nodes
            G.remove_nodes_from(list(nx.isolates(G)))

            # Calculate node centrality
            if len(G.nodes()) > 0:
                centrality = nx.degree_centrality(G)
                nx.set_node_attributes(G, centrality, 'centrality')

            return G
        except Exception as e:
            print(f"Error building keyword network: {str(e)}")
            return None