import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from utils.data_processor import DataProcessor
from utils.text_analysis import TextAnalyzer
from utils.visualizations import Visualizer
import networkx as nx
import matplotlib.pyplot as plt
from streamlit_plotly_events import plotly_events  # <-- For capturing clicks
from wordcloud import WordCloud

# import streamlit as st

# st.set_page_config(
#     page_title="Authors Discovery",
#     page_icon="👥",
#     layout="wide",
# )

# Check if data is initialized
if 'data_processor' not in st.session_state:
    st.error("Please initialize the app from the Home page")
    st.stop()

st.title("Authors Discovery 👥")

# Rest of your authors discovery code...


# st.set_page_config(page_title="Authors Discovery", layout="wide")

# Initialize session state if not already done in main.py
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor('attached_assets/df.xlsx')
    st.session_state.text_analyzer = TextAnalyzer(st.session_state.data_processor.df)
    st.session_state.visualizer = Visualizer()


# Row 1: Author Search
st.subheader("Author Search 🔍")
search_query = st.text_input("Search for an author")

# Row 2: Author-Level Metrics
col1, col2, col3, col4 = st.columns(4)
total_authors = st.session_state.data_processor.df['author_list'].explode().nunique()
single_authored = len(st.session_state.data_processor.df[
    st.session_state.data_processor.df['author_list'].apply(len) == 1
])
multi_authored = len(st.session_state.data_processor.df[
    st.session_state.data_processor.df['author_list'].apply(len) > 1
])
total_citations = st.session_state.data_processor.df['citations'].sum()

with col1:
    st.metric("Total Authors 👤", total_authors)
with col2:
    st.metric("Single-Authored Documents ✍️", single_authored)
with col3:
    st.metric("Multi-Authored Documents 👥", multi_authored)
with col4:
    st.metric("Total Citations 📚", total_citations)

# Row 3: Top Authors Over Time
st.subheader("Top Authors Over Time 📈")
top_authors_df = st.session_state.data_processor.df.explode('author_list')
top_authors = top_authors_df.groupby(['author_list', 'year']).size().reset_index(name='publications')
top_20_authors = top_authors_df['author_list'].value_counts().head(20).index

fig_authors_time = px.line(
    top_authors[top_authors['author_list'].isin(top_20_authors)],
    x='year',
    y='publications',
    color='author_list',
    title='Publication Trends of Top 20 Authors'
)
st.plotly_chart(fig_authors_time, use_container_width=True)


# Row 4: Author Collaboration Network
st.subheader("Author Collaboration Network 🕸️")

with st.spinner("Generating collaboration network..."):
    # Get top authors to limit the network size
    @st.cache_data
    def get_top_authors(df, n=500):
        return (df['author_list']
                .explode()
                .value_counts()
                .head(n)
                .index
                .tolist())
    
    # Get the top authors
    top_authors = get_top_authors(st.session_state.data_processor.df)
    
    # Build network graph based on co-authorship
    G = nx.Graph()
    
    for authors in st.session_state.data_processor.df['author_list'].dropna():
        if isinstance(authors, list):
            # Filter for top authors only
            valid_authors = [author for author in authors if author in top_authors]
            
            # Add edges between all pairs of authors
            for i in range(len(valid_authors)):
                for j in range(i+1, len(valid_authors)):
                    if valid_authors[i] != valid_authors[j]:
                        G.add_edge(valid_authors[i], valid_authors[j])
    
    if len(G.nodes()) > 0:
        # Create the visualization
        plt.figure(figsize=(15, 10))
        pos = nx.spring_layout(G, k=0.5, iterations=50)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='lightgray', alpha=0.5)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, 
                             node_color='lightblue',
                             node_size=100,
                             alpha=0.7)
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, 
                              font_size=8,
                              font_family='sans-serif')
        
        plt.title("Author Collaboration Network", pad=20)
        plt.axis('off')
        
        # Display in Streamlit
        st.pyplot(plt)
        plt.close()
        
        # Display some basic network statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Number of Authors", len(G.nodes()))
        with col2:
            st.metric("Total Collaborations", len(G.edges()))
        with col3:
            avg_collaborators = sum(dict(G.degree()).values()) / len(G.nodes())
            st.metric("Avg. Collaborators", f"{avg_collaborators:.1f}")
    else:
        st.warning("No collaboration network available")

st.markdown("---")




# Row 5: Document Discovery
# st.subheader("Document Discovery")


col1, col2 = st.columns([1, 2])

with col1:
    # Bubble plot for top 20 authors
    author_stats = top_authors_df.groupby('author_list').agg({
        'citations': 'sum',
        'year': 'count'
    }).reset_index()
    author_stats = author_stats.nlargest(20, 'citations')

    fig_bubble = px.scatter(
        author_stats,
        x='year',
        y='citations',
        size='citations',
        text='author_list',
        title='Top 20 Authors by Citations and Publications'
    )
    # st.plotly_chart(fig_bubble, use_container_width=True)

st.header("Detailed Author Publications 📑")

# Row 6: Top 20 Authors Articles
st.subheader("Articles by Top 20 Authors 📊")

# Get top 20 authors
top_20_authors_list = author_stats['author_list'].tolist()

# After your bubble plot code, add:



# Create selectbox for author selection
selected_author = st.selectbox(
    "Select an author to view their publications",
    top_20_authors_list,
    key="author_select"
)

if selected_author:
    # Get author's papers
    author_papers = st.session_state.data_processor.df[
        st.session_state.data_processor.df['author_list'].apply(
            lambda x: selected_author in x if isinstance(x, list) else False
        )
    ]
    
    # Sort papers by year and citations
    author_papers = author_papers.sort_values(
        by=['year', 'citations'],
        ascending=[False, False]
    )
    
    # Show author stats in a more visually appealing way
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Publications", len(author_papers))
    with col2:
        st.metric("Total Citations", author_papers['citations'].sum())
    with col3:
        avg_citations = round(author_papers['citations'].mean(), 1)
        st.metric("Average Citations per Paper", avg_citations)
    
    # Add a filter for years
    years = sorted(author_papers['year'].unique(), reverse=True)
    selected_years = st.multiselect(
        "Filter by years",
        years,
        default=years,
        key="year_filter"
    )
    
    # Filter papers by selected years
    filtered_papers = author_papers[author_papers['year'].isin(selected_years)]

    # After the year filter and before the search box:

    # Create word clouds for abstracts and titles
    if filtered_papers is not None and not filtered_papers.empty:
        st.subheader("Content Analysis")
        wc_col1, wc_col2 = st.columns(2)
        
        with wc_col1:
            st.write("**Abstract Word Cloud**")
            # Combine all abstracts
            abstracts_text = ' '.join(filtered_papers['abstract'].dropna().astype(str))
            if abstracts_text.strip():
                # Generate word cloud
                wordcloud_abstracts = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    colormap='viridis',
                    max_words=100,
                    min_font_size=10,
                    font_path='attached_assets/CabinSketch-Bold.ttf' 
                ).generate(abstracts_text)
                
                # Display word cloud
                fig_abs = plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud_abstracts, interpolation='bilinear')
                plt.axis('off')
                st.pyplot(fig_abs)
            else:
                st.info("No abstract text available for the selected papers")
        
        with wc_col2:
            st.write("**Title Word Cloud**")
            # Combine all titles
            titles_text = ' '.join(filtered_papers['title'].dropna().astype(str))
            if titles_text.strip():
                # Generate word cloud
                wordcloud_titles = WordCloud(
                    width=800,
                    height=400,
                    background_color='white',
                    colormap='plasma',  # Different colormap to distinguish from abstracts
                    max_words=50,  # Fewer words for titles as they're shorter
                    min_font_size=10,
                    font_path='attached_assets/CabinSketch-Bold.ttf' 
                ).generate(titles_text)
                
                # Display word cloud
                fig_titles = plt.figure(figsize=(10, 5))
                plt.imshow(wordcloud_titles, interpolation='bilinear')
                plt.axis('off')
                st.pyplot(fig_titles)
            else:
                st.info("No titles available for the selected papers")
        
        # Add some basic text statistics
        st.subheader("Text Statistics")
        stats_col1, stats_col2, stats_col3 = st.columns(3)
        
        with stats_col1:
            avg_abstract_len = filtered_papers['abstract'].dropna().str.split().str.len().mean()
            st.metric("Avg. Words per Abstract", f"{avg_abstract_len:.0f}")
        
        with stats_col2:
            avg_title_len = filtered_papers['title'].dropna().str.split().str.len().mean()
            st.metric("Avg. Words per Title", f"{avg_title_len:.0f}")
        
        with stats_col3:
            total_papers = len(filtered_papers)
            papers_with_abstract = filtered_papers['abstract'].notna().sum()
            abstract_coverage = (papers_with_abstract / total_papers) * 100
            st.metric("Abstract Coverage", f"{abstract_coverage:.1f}%")

    # Continue with the existing search box and paper display...
    
    # Add a search box for paper titles
    search_term = st.text_input(
        "Search in titles",
        key="paper_search"
    )
    
    if search_term:
        filtered_papers = filtered_papers[
            filtered_papers['title'].str.contains(search_term, case=False, na=False)
        ]
    
    # Display count of shown papers
    st.write(f"Showing {len(filtered_papers)} papers")

    # Option 3: Using a caption and info combination
    st.caption("Studies are sorted by year and citation count")
    st.info("🔍 Click to expand and view abstract, authors, and other details")
    
    # Display papers in expandable sections
    for _, paper in filtered_papers.iterrows():
        with st.expander(f"{paper['year']} - {paper['title']} (Citations: {paper['citations']})"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Article metadata
                st.markdown(f"**Year:** {paper['year']}")
                st.markdown(f"**Journal:** {paper['journal']}")
                
                # Authors with highlighting
                authors = paper['author_list']
                if isinstance(authors, list):
                    highlighted_authors = [
                        f"**{auth}**" if auth == selected_author else auth
                        for auth in authors
                    ]
                    st.markdown("**Authors:** " + ", ".join(highlighted_authors))
                
                # Keywords
                if isinstance(paper['author_keywords'], str):
                    st.markdown("**Keywords:** " + paper['author_keywords'])
                
                # Abstract
                if isinstance(paper['abstract'], str):
                    st.markdown("**Abstract:**")
                    st.markdown(f">{paper['abstract']}")
            
            with col2:
                # Citations and DOI in a card-like format
                st.markdown("""
                <style>
                .citation-card {
                    padding: 1rem;
                    background-color: #f8f9fa;
                    border-radius: 0.5rem;
                    margin-bottom: 1rem;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class='citation-card'>
                    <h4>Citation Metrics</h4>
                    <p>Citations: {paper['citations']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # DOI link
                if isinstance(paper['doi'], str):
                    st.markdown(f"**DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")
else:
    st.info("Please select an author to view their publications")

with col2:
    if search_query:
        matched_authors = top_authors_df['author_list'][
            top_authors_df['author_list'].str.contains(search_query, case=False, na=False)
        ].unique()

        if len(matched_authors) > 0:
            selected_author = st.selectbox("Select an author", matched_authors)

            # Author's keyword word cloud
            st.write("### Author Keywords")
            author_papers = st.session_state.data_processor.df[
                st.session_state.data_processor.df['author_list'].apply(
                    lambda x: selected_author in x if isinstance(x, list) else False
                )
            ]

            # Publication timeline for selected author
            yearly_pubs = author_papers.groupby('year').size().reset_index(name='publications')
            fig_timeline = px.line(
                yearly_pubs,
                x='year',
                y='publications',
                title=f'Publication Timeline for {selected_author}'
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

            # Author-specific articles section
            st.subheader(f"Articles by {selected_author}")

            # Sort papers by year (most recent first) and citations
            author_papers = author_papers.sort_values(
                by=['year', 'citations'],
                ascending=[False, False]
            )

            # Display articles in expandable sections
            for _, paper in author_papers.iterrows():
                with st.expander(f"{paper['year']} - {paper['title']}"):
                    # Article metadata
                    st.markdown(f"**Year:** {paper['year']}")
                    st.markdown(f"**Journal:** {paper['journal']}")
                    st.markdown(f"**Citations:** {paper['citations']}")

                    # Authors with highlighting for selected author
                    authors = paper['author_list']
                    if isinstance(authors, list):
                        highlighted_authors = [
                            f"**{author}**" if author == selected_author else author
                            for author in authors
                        ]
                        st.markdown("**Authors:** " + ", ".join(highlighted_authors))

                    # Keywords if available
                    if isinstance(paper['author_keywords'], str):
                        st.markdown("**Keywords:** " + paper['author_keywords'])

                    # Abstract with a distinct visual separation
                    st.markdown("**Abstract:**")
                    st.markdown(f">{paper['abstract']}")

                    # Additional metadata if available
                    if isinstance(paper['doi'], str):
                        st.markdown(f"**DOI:** [{paper['doi']}](https://doi.org/{paper['doi']})")

        else:
            st.warning("No authors found matching the search query.")



