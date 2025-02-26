import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import networkx as nx
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import pyLDAvis
import pyLDAvis.lda_model

# Add scipy compatibility check
import scipy
from packaging import version
scipy_version = version.parse(scipy.__version__)
SCIPY_COMPATIBLE = scipy_version >= version.parse('1.8.0')
from utils.data_processor import DataProcessor
from utils.text_analysis import TextAnalyzer
from utils.visualizations import Visualizer
import nltk
from collections import defaultdict
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import io
import base64
import random

# Streamlit page config
st.title("Topic Discovery 🔍")

# Check if data is initialized
if 'data_processor' not in st.session_state:
    st.error("Please initialize the app from the Home page")
    st.stop()

# Sidebar controls
with st.sidebar:
    st.header("Topic Modeling Parameters ⚙️")
    
    # Add the option to choose preprocessing method
    preprocessing_method = st.radio(
        "Text Preprocessing Method",
        ["Standard", "Advanced (with lemmatization & n-grams)"],
        index=1,  # Default to advanced
        help="Advanced preprocessing includes lemmatization and detection of multi-word phrases"
    )
    
    # Make sure NLTK resources are downloaded if using advanced method
    if preprocessing_method == "Advanced (with lemmatization & n-grams)":
        with st.spinner("Setting up language processing resources..."):
            try:
                # Download necessary NLTK resources
                nltk.download('wordnet', quiet=True)
                nltk.download('stopwords', quiet=True)
                nltk.download('punkt', quiet=True)
            except Exception as e:
                st.warning(f"Could not download some NLTK resources: {e}. Some features may be limited.")
    
    n_topics = st.slider("Number of Topics", min_value=3, max_value=20, value=10)
    
    with st.expander("Advanced Parameters"):
        learning_method = st.selectbox(
            "Learning Method",
            ["online", "batch"],
            help="Online learning is faster for large datasets"
        )
        max_iter = st.slider("Maximum Iterations", min_value=5, max_value=50, value=10)
        n_jobs = st.selectbox(
            "Number of Jobs",
            [1, 2, 4, -1],
            index=3,
            help="Number of parallel jobs (-1 uses all cores)"
        )
        
        if preprocessing_method == "Advanced (with lemmatization & n-grams)":
            min_token_length = st.slider("Minimum Token Length", min_value=2, max_value=5, value=3, 
                                       help="Tokens shorter than this will be removed")
            min_word_frequency = st.slider("Minimum Word Frequency", min_value=2, max_value=20, value=5,
                                         help="Words appearing in fewer documents than this will be filtered")
            max_word_frequency = st.slider("Maximum Word Frequency (%)", min_value=10, max_value=95, value=20,
                                         help="Words appearing in more documents than this percentage will be filtered")

# Topic Modeling Analysis
st.header("Topic Modeling Analysis 📊", divider="rainbow")

use_advanced = preprocessing_method == "Advanced (with lemmatization & n-grams)"

# Run topic modeling with selected parameters
with st.spinner(f"Analyzing topics using {preprocessing_method} preprocessing..."):
    # Add progress indicator for advanced preprocessing
    if use_advanced:
        progress_bar = st.progress(0)
        st.info("Advanced preprocessing includes lemmatization and detection of multi-word phrases. This may take a moment...")
        progress_bar.progress(25)
    
    # Run topic modeling
    topic_results = st.session_state.text_analyzer.extract_topics(
        n_topics=n_topics,
        learning_method=learning_method,
        max_iter=max_iter,
        n_jobs=n_jobs,
        use_advanced_preprocessing=use_advanced
    )
    
    if use_advanced:
        progress_bar.progress(100)
        st.success("Advanced preprocessing complete!")
        
        # Show vocabulary metrics if using advanced preprocessing
        if topic_results.get('dictionary'):
            dictionary = topic_results['dictionary']
            corpus = topic_results['corpus']
            st.caption(f"✓ Processed {len(dictionary)} unique terms after filtering")
            st.caption(f"✓ Identified multi-word phrases (bigrams & trigrams)")
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Topic Coherence 🎯", f"{topic_results['coherence_score']:.2f}")
    with col2:
        st.metric("Topic Diversity 🌈", f"{topic_results['topic_diversity']:.2f}")
    with col3:
        st.metric("Model Perplexity 🧮", f"{topic_results['perplexity']:.2f}")

# Topic Visualizations in Tabs
st.header("Topic Visualization Dashboard 📊", divider="rainbow")

tab1, tab2, tab3, tab4 = st.tabs([
    "🔤 Word Clouds", 
    "🔠 Multi-word Phrases", 
    "📈 Topic Trends", 
    "🧩 Document-Topic Distribution"
])

# Tab 1: Word Clouds of Top Keywords in Each Topic
with tab1:
    st.subheader("🔤 Word Clouds of Top Keywords in Each Topic", divider="rainbow")
    if topic_results['topics']:
        # Function to create and save word cloud
        def create_wordcloud(topic_words, topic_num, colormap='tab10'):
            # Create word cloud
            wc = WordCloud(
                background_color='white',
                width=800,
                height=400,
                max_words=15,
                colormap=colormap,
                prefer_horizontal=1.0,
                font_path='attached_assets/CabinSketch-Bold.ttf' 
            )
            
            # Generate from frequencies
            wc.generate_from_frequencies(topic_words)
            
            # Create figure and plot
            fig, ax = plt.subplots(figsize=(10, 5))
            ax.imshow(wc, interpolation='bilinear')
            # Increased font size for topic title
            ax.set_title(f'Topic {topic_num + 1}', fontdict=dict(size=24, weight='bold'))
            ax.axis('off')
            plt.tight_layout()
            
            # Save to buffer
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', pad_inches=0.1)
            plt.close(fig)
            buf.seek(0)
            
            # Return encoded image
            return base64.b64encode(buf.read()).decode()
        
        # Determine number of columns for layout (1, 2, or 3 based on number of topics)
        num_cols = min(3, n_topics)
        
        # Create a grid of word clouds
        for i in range(0, n_topics, num_cols):
            cols = st.columns(num_cols)
            
            for j in range(num_cols):
                topic_idx = i + j
                if topic_idx < n_topics:
                    topic_name = f"Topic {topic_idx + 1}"
                    # Get word-weight pairs
                    topic_words = dict(zip(
                        topic_results['topics'][topic_name]['words'],
                        topic_results['topics'][topic_name]['weights']
                    ))
                    
                    # Replace underscores with spaces for better display
                    topic_words = {word.replace('_', ' '): weight for word, weight in topic_words.items()}
                    
                    # Create word cloud and get encoded image
                    img_str = create_wordcloud(topic_words, topic_idx)
                    
                    # Display in column - Fixed deprecated parameter
                    cols[j].image(f"data:image/png;base64,{img_str}", use_container_width=True)
    else:
        st.warning("No topic data available. Please run topic modeling first.")

# Tab 2: Multi-word Phrases Detected
with tab2:
    st.subheader("🔠 Multi-word Phrases Detected in the Corpus", divider="rainbow")
    
    if use_advanced and topic_results.get('dictionary'):
        # Extract n-grams from the dictionary
        ngrams = [term for term in topic_results['dictionary'].token2id.keys() if '_' in term]
        
        if ngrams:
            # Count frequency of each n-gram in corpus
            ngram_freqs = {}
            for doc_bow in topic_results['corpus']:
                for term_id, freq in doc_bow:
                    term = topic_results['dictionary'][term_id]
                    if '_' in term:
                        ngram_freqs[term] = ngram_freqs.get(term, 0) + freq
            
            # Sort by frequency
            sorted_ngrams = sorted(ngram_freqs.items(), key=lambda x: x[1], reverse=True)
            
            # Display top phrases as treemap
            if len(sorted_ngrams) > 0:
                # Convert to DataFrame
                ngram_df = pd.DataFrame(sorted_ngrams, columns=['Phrase', 'Frequency'])
                
                # Replace underscores with spaces for better display
                ngram_df['Phrase'] = ngram_df['Phrase'].apply(lambda x: x.replace('_', ' '))
                
                # Limit to top 50 for cleaner visualization
                if len(ngram_df) > 50:
                    ngram_df = ngram_df.head(50)
                    st.caption(f"Showing top 50 out of {len(sorted_ngrams)} multi-word phrases")
                
                # Group by first word to create hierarchy for treemap
                hierarchy = defaultdict(dict)
                
                for ngram, freq in zip(ngram_df['Phrase'], ngram_df['Frequency']):
                    parts = ngram.split()
                    if len(parts) > 1:
                        first_word = parts[0]
                        rest = ' '.join(parts[1:])
                        hierarchy[first_word][rest] = freq
                    else:
                        hierarchy[ngram] = {'': freq}
                
                # Prepare data for treemap
                labels = []
                parents = []
                values = []
                
                # Add top level (first word) nodes
                for first_word, items in hierarchy.items():
                    labels.append(first_word)
                    parents.append('')
                    # Sum of all children values
                    values.append(sum(items.values()))
                    
                    # Add child nodes
                    for rest, value in items.items():
                        if rest:  # Skip empty items
                            labels.append(f"{first_word} {rest}")
                            parents.append(first_word)
                            values.append(value)
                
                # Create treemap
                fig = go.Figure(go.Treemap(
                    labels=labels,
                    parents=parents,
                    values=values,
                    textinfo="label+value",
                    hoverinfo="label+value+percent parent+percent root",
                    marker=dict(
                        colorscale='Viridis',
                        showscale=True
                    ),
                    pathbar=dict(
                        visible=True
                    )
                ))
                
                fig.update_layout(
                    title="Treemap of Multi-word Phrases",
                    height=500,
                    margin=dict(t=50, l=25, r=25, b=25)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Show total count
                st.caption(f"Detected {len(sorted_ngrams)} multi-word phrases in the corpus")
            else:
                st.info("No multi-word phrases met the frequency criteria")
        else:
            st.info("No multi-word phrases detected in the corpus")
    else:
        st.info("Advanced preprocessing with n-gram detection is required to view multi-word phrases. Please select 'Advanced' preprocessing method in the sidebar.")

# Tab 3: Topic Trends Visualization
with tab3:
    st.subheader("📈 Topic Prevalence Over Time", divider="rainbow")
    yearly_trends = st.session_state.text_analyzer.get_topic_trends(topic_results['doc_topics'])

    if not yearly_trends.empty:
        fig_trends = px.line(
            yearly_trends,
            title="Evolution of Topic Prevalence Over Years",
            labels={"value": "Topic Proportion", "variable": "Topic"}
        )
        fig_trends.update_layout(
            height=500,
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_trends, use_container_width=True)
        
        # Add explanatory text
        st.info("""
        This chart shows how the prevalence of each topic changes over time.
        - Each line represents a topic
        - The y-axis shows the average topic proportion across documents in that year
        - Rising lines indicate growing interest in a topic
        - Declining lines suggest waning interest in that topic area
        """)
        
        # Add a table view of the data
        with st.expander("View Topic Trends Data Table"):
            st.dataframe(yearly_trends)
    else:
        st.warning("No yearly trend data available. This may occur if your dataset lacks year information for documents.")

# Tab 4: Document-Topic Distribution Heatmap
with tab4:
    st.subheader("🧩 Document-Topic Distribution Heatmap", divider="rainbow")
    if topic_results['doc_topics'] is not None:
        df = st.session_state.data_processor.df
        vectorizer = st.session_state.text_analyzer.vectorizer
        lda_model = st.session_state.text_analyzer.lda_model
        
        if 'abstract' in df.columns and vectorizer and lda_model:
            # Get a list of documents with non-empty abstracts
            docs_with_abstracts = df[df['abstract'].notna() & (df['abstract'] != '')].copy()
            
            if len(docs_with_abstracts) > 0:
                # Allow user to select number of documents to display
                num_docs = st.slider("Number of documents to display", 5, min(20, len(docs_with_abstracts)), 10)
                
                # Randomly select documents
                sample_docs = docs_with_abstracts.sample(num_docs)
                
                # Process each document to get topic distribution
                doc_data = []
                
                for idx, doc in sample_docs.iterrows():
                    # Get tokens from the abstract
                    tokens = nltk.word_tokenize(doc['abstract'].lower())
                    filtered_tokens = [t for t in tokens if t.isalpha() and 
                                    t not in st.session_state.text_analyzer.stop_words and 
                                    len(t) > 3]
                    
                    # Count topic distributions for each token
                    topic_counts = np.zeros(n_topics)
                    total_tokens = 0
                    
                    for token in filtered_tokens:
                        dtm = vectorizer.transform([token])
                        if dtm.sum() > 0:  # Only if token is in vocabulary
                            topic_dist = lda_model.transform(dtm)[0]
                            dominant_topic = np.argmax(topic_dist)
                            topic_counts[dominant_topic] += 1
                            total_tokens += 1
                    
                    # Normalize by total tokens
                    if total_tokens > 0:
                        topic_counts = topic_counts / total_tokens
                    
                    # Add document info
                    title = doc.get('title', f'Document {idx}')
                    # Truncate if too long
                    if len(title) > 40:
                        title = title[:37] + "..."
                        
                    doc_data.append({
                        'doc_id': len(doc_data) + 1,
                        'title': title,
                        'year': doc.get('year', 'Unknown'),
                        'topic_dist': topic_counts
                    })
                
                # Create heatmap data
                x_labels = [f'Topic {i+1}' for i in range(n_topics)]
                y_labels = [f"Doc {d['doc_id']} ({d['year']}): {d['title']}" for d in doc_data]
                z_values = [d['topic_dist'] for d in doc_data]
                
                # Create heatmap figure
                fig = px.imshow(
                    z_values,
                    x=x_labels,
                    y=y_labels,
                    color_continuous_scale='Blues',
                    aspect='auto',
                    labels=dict(x='Topic', y='Document', color='Proportion of Words')
                )
                
                # Update layout
                fig.update_layout(
                    height=max(400, 30 * len(doc_data)),  # Adjust height based on number of documents
                    margin=dict(l=20, r=20, t=50, b=20),
                    coloraxis_colorbar=dict(
                        title=dict(
                            text="Proportion",
                            side="right",
                            font=dict(size=14)
                        ),
                        tickfont=dict(size=12)
                    )
                )
                
                # Add annotations for top topic in each document
                for i, doc_topics in enumerate(z_values):
                    top_topic_idx = np.argmax(doc_topics)
                    top_topic_val = doc_topics[top_topic_idx]
                    
                    if top_topic_val > 0:
                        fig.add_annotation(
                            x=top_topic_idx,
                            y=i,
                            text=f"{top_topic_val:.2f}",
                            showarrow=False,
                            font=dict(
                                color="white" if top_topic_val > 0.3 else "black",
                                size=10
                            )
                        )
                
                # Display the heatmap
                st.plotly_chart(fig, use_container_width=True)
                
                # Add explanation
                st.info("""
                This heatmap shows how words in each document are distributed across topics.
                - Each row represents a document
                - Each column represents a topic
                - The color intensity indicates what proportion of words in the document are attributed to each topic
                - Darker blue indicates a higher proportion of words belong to that topic
                - Numbers in cells show the proportion value for the dominant topic in each document
                """)
            else:
                st.warning("No documents with abstracts found in the dataset.")
        else:
            st.warning("Abstract data, vectorizer, or LDA model not available.")
    else:
        st.warning("Topic modeling did not produce valid results.")

# LDA Visualization
st.header("Topic Model Visualization 📈", divider="rainbow")
with st.spinner("Preparing interactive visualization..."):
    if topic_results['doc_topics'] is not None:
        df = st.session_state.data_processor.df
        texts = df['title'].fillna('') + ' ' + df['abstract'].fillna('')
        texts = texts.dropna()

        if len(texts) > 0:
            vectorizer = st.session_state.text_analyzer.vectorizer
            lda_model = st.session_state.text_analyzer.lda_model
            
            if vectorizer and lda_model:
                dtm = vectorizer.transform(st.session_state.text_analyzer.df['processed_text'])
                
                # Create pyLDAvis visualization
                panel = pyLDAvis.lda_model.prepare(lda_model, dtm, vectorizer, mds='tsne')
                html_string = pyLDAvis.prepared_data_to_html(panel)
                st.components.v1.html(html_string, width=None, height=800, scrolling=True)
            else:
                st.warning("Could not create visualization due to incomplete model preparation")

# Topic-Specific Articles
st.header("Topic-Specific Articles 📚", divider="rainbow")
if topic_results['doc_topics'] is not None:
    # Initialize articles per page state if not exists
    if 'articles_per_page' not in st.session_state:
        st.session_state.articles_per_page = 10

    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col1:
        selected_topic_idx = st.selectbox(
            "Select Topic to Explore 🔍",
            range(n_topics),
            format_func=lambda x: f"Topic {x+1}",
            key="topic_selector"
        )
        prob_threshold = st.slider(
            "Minimum Topic Probability",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.05,
            key="prob_threshold"
        )

    # Show topic keywords
    with col2:
        topic_words = topic_results['topics'][f"Topic {selected_topic_idx + 1}"]['words']
        st.markdown(f"**Top Words for Topic {selected_topic_idx + 1}:**")
        
        # Display multi-word phrases nicely (replace underscore with space)
        formatted_words = [word.replace('_', ' ') for word in topic_words]
        st.markdown(f"*{', '.join(formatted_words)}*")

    # Show topic metrics in col3
    with col3:
        st.markdown("**Topic Metrics**")
        
        # Calculate metrics for the selected topic
        topic_probs = topic_results['doc_topics'][:, selected_topic_idx]
        total_docs = len(topic_probs)
        docs_above_threshold = sum(topic_probs >= prob_threshold)
        avg_probability = np.mean(topic_probs)
        
        # Create three metrics in the third column
        st.metric(
            "Total Documents 📄",
            f"{docs_above_threshold}/{total_docs}",
            f"{(docs_above_threshold/total_docs)*100:.1f}%"
        )
        
        st.metric(
            "Average Topic Probability 📊",
            f"{avg_probability:.3f}"
        )
        
        # Calculate dominant topic count
        dominant_topic_mask = np.argmax(topic_results['doc_topics'], axis=1) == selected_topic_idx
        dominant_docs = sum(dominant_topic_mask)
        st.metric(
            "Documents where Topic is Dominant 📈",
            f"{dominant_docs}",
            f"{(dominant_docs/total_docs)*100:.1f}%"
        )

    # Filter and display relevant articles
    topic_probs = topic_results['doc_topics'][:, selected_topic_idx]
    relevant_docs_mask = topic_probs >= prob_threshold
    relevant_docs = df[relevant_docs_mask].copy()
    relevant_docs['topic_probability'] = topic_probs[relevant_docs_mask]
    relevant_docs = relevant_docs.sort_values('topic_probability', ascending=False)

    if len(relevant_docs) > 0:
        total_articles = len(relevant_docs)
        st.caption(f"Found {total_articles} relevant articles")
        st.info("🔍 Click to expand and view abstract, authors, and other details")

        # Display only the first n articles
        articles_to_show = relevant_docs.iloc[:st.session_state.articles_per_page]
        
        for idx, article in articles_to_show.iterrows():
            with st.expander(
                f"{article['year']} - {article['title']} "
                f"(Topic Probability: {article['topic_probability']:.2f})"
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown("**Article Details: 📝**")
                    st.markdown(f"**Year: 📅** {article['year']}")
                    st.markdown(f"**Authors: 👥** {', '.join(article['author_list']) if isinstance(article['author_list'], list) else article['author']}")
                    st.markdown(f"**Journal: 📰** {article['journal']}")
                    if isinstance(article['abstract'], str):
                        st.markdown("**Abstract: 📄**")
                        st.markdown(f">{article['abstract']}")
                    if isinstance(article['doi'], str):
                        st.markdown(f"**DOI: 🔗** [{article['doi']}](https://doi.org/{article['doi']})")

                with col2:
                    article_topics = topic_results['doc_topics'][idx]
                    fig = go.Figure(data=[
                        go.Bar(
                            x=[f"Topic {i+1}" for i in range(len(article_topics))],
                            y=article_topics,
                            text=[f"{v:.2f}" for v in article_topics],
                            textposition='auto'
                        )
                    ])
                    fig.update_layout(
                        title="Topic Distribution",
                        xaxis_title="Topics",
                        yaxis_title="Probability",
                        height=300,
                        margin=dict(l=10, r=10, t=30, b=10)
                    )
                    st.plotly_chart(fig, use_container_width=True, key=f"topic_dist_{idx}")

        # Show load more button if there are more articles
        remaining_articles = total_articles - st.session_state.articles_per_page
        if remaining_articles > 0:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"📥 Load More ({remaining_articles} articles remaining)",
                    key="load_more"
                ):
                    st.session_state.articles_per_page += 10
                    st.rerun()
                
                # Add reset button
                if st.session_state.articles_per_page > 10:
                    if st.button("🔄 Reset View", key="reset_view"):
                        st.session_state.articles_per_page = 10
                        st.rerun()
    else:
        st.warning(f"No articles found with topic probability >= {prob_threshold}")