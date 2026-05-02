import streamlit as st
import pandas as pd
from utils.data_processor import DataProcessor
from utils.text_analysis import TextAnalyzer
from utils.visualizations import Visualizer

# Page config
# st.set_page_config(
#     page_title="References Explorer",
#     page_icon="📖",
#     layout="wide",
# )

# Initialize session state
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor('attached_assets/df.xlsx')
    st.session_state.text_analyzer = TextAnalyzer(st.session_state.data_processor.df)
    st.session_state.visualizer = Visualizer()

# Initialize refs_per_page state if not exists
if 'refs_per_page' not in st.session_state:
    st.session_state.refs_per_page = {}

st.title("References Explorer  📚")

# Get the dataframe
df = st.session_state.data_processor.df

# Sidebar filters
with st.sidebar:
    st.header("Filter References 🔍")
    
    # Year range filter
    years = sorted(df['year'].dropna().unique())
    year_range = st.slider(
        "Select Year Range 📅",
        min_value=int(min(years)),
        max_value=int(max(years)),
        value=(int(min(years)), int(max(years))),
        key="year_filter"
    )
    
    # Journal filter
    journals = sorted(df['journal'].dropna().unique())
    selected_journals = st.multiselect(
        "Select Journals 📰",
        journals,
        default=[],
        key="journal_filter"
    )
    
    # Country filter
    countries = sorted(df['countries'].dropna().unique())
    selected_countries = st.multiselect(
        "Select Countries 🌍",
        countries,
        default=[],
        key="country_filter"
    )
    
    # Citations filter
    min_citations = st.number_input(
        "Minimum Citations 📊",
        min_value=0,
        value=0,
        key="citation_filter"
    )

    # Sort order
    sort_order = st.selectbox(
        "Sort By",
        ["Year (Newest First)", "Year (Oldest First)", "Citations (Highest First)", "Citations (Lowest First)"],
        key="sort_order"
    )

# Apply filters
filtered_df = df.copy()

# Year filter
filtered_df = filtered_df[
    (filtered_df['year'] >= year_range[0]) &
    (filtered_df['year'] <= year_range[1])
]

# Journal filter
if selected_journals:
    filtered_df = filtered_df[filtered_df['journal'].isin(selected_journals)]

# Country filter
if selected_countries:
    filtered_df = filtered_df[filtered_df['countries'].isin(selected_countries)]

# Citations filter
filtered_df = filtered_df[filtered_df['citations'] >= min_citations]

# Apply sorting
if sort_order == "Year (Newest First)":
    filtered_df = filtered_df.sort_values(['year', 'citations'], ascending=[False, False])
elif sort_order == "Year (Oldest First)":
    filtered_df = filtered_df.sort_values(['year', 'citations'], ascending=[True, False])
elif sort_order == "Citations (Highest First)":
    filtered_df = filtered_df.sort_values(['citations', 'year'], ascending=[False, False])
else:  # Citations (Lowest First)
    filtered_df = filtered_df.sort_values(['citations', 'year'], ascending=[True, False])

# Display metrics
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total References 📚", len(filtered_df))
with col2:
    st.metric("Total Citations 📝", filtered_df['citations'].sum())
with col3:
    avg_citations = round(filtered_df['citations'].mean(), 2)
    st.metric("Average Citations 📊", avg_citations)
with col4:
    unique_journals = len(filtered_df['journal'].unique())
    st.metric("Unique Journals 📰", unique_journals)

# Search box
search_query = st.text_input(
    "🔍 Search in titles, abstracts, or keywords",
    key="search_box"
)

# Add custom CSS for styling
st.markdown("""
<style>
.metric-card {
    background-color: #f0f2f6;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 10px;
}
.keyword-pill {
    background-color: #e0e0e0;
    padding: 2px 8px;
    border-radius: 12px;
    margin-right: 5px;
    display: inline-block;
    margin-bottom: 5px;
}
.year-section {
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #e0e0e0;
}
</style>
""", unsafe_allow_html=True)

# Group by year and create reference list
years = sorted(filtered_df['year'].unique(), reverse=True)

for year in years:
    year_df = filtered_df[filtered_df['year'] == year]
    
    # Apply search filter if exists
    if search_query:
        mask = (
            year_df['title'].str.contains(search_query, case=False, na=False) |
            year_df['abstract'].str.contains(search_query, case=False, na=False) |
            year_df['author_keywords'].str.contains(search_query, case=False, na=False)
        )
        year_df = year_df[mask]
    
    if len(year_df) > 0:
        # Initialize refs_per_page for this year if not exists
        if year not in st.session_state.refs_per_page:
            st.session_state.refs_per_page[year] = 10
            
        total_refs = len(year_df)
        
        st.markdown(f"""
        <div class='year-section'>
            <h2>{year} ({total_refs} references)</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Get references to show for this year
        refs_to_show = year_df.iloc[:st.session_state.refs_per_page[year]]
        
        for idx, ref in refs_to_show.iterrows():
            with st.expander(f"📚 {ref['title']} (Citations: {ref['citations']})"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown("#### 📄 Article Details")
                    st.markdown(f"**Journal:** 📰  {ref['journal']}")
                    st.markdown("**Authors:** 👥" + 
                              ', '.join(ref['author_list']) if isinstance(ref['author_list'], list) 
                              else ref['author'])
                    
                    if isinstance(ref['abstract'], str):
                        st.markdown("**Abstract:** 📝")
                        st.markdown(f">{ref['abstract']}")
                    
                    if isinstance(ref['author_keywords'], str):
                        st.markdown("**Keywords:** 🏷️")
                        keywords = [kw.strip() for kw in ref['author_keywords'].split(';')]
                        keyword_html = ' '.join([
                            f'<span class="keyword-pill">{kw}</span>'
                            for kw in keywords
                        ])
                        st.markdown(keyword_html, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 📊 Metrics & Links")
                    st.markdown(f"""
                    <div class="metric-card">
                        <h5>📈 Citations: {ref['citations']}</h5>
                        <p>🌍 Country: {ref['countries']}</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    if isinstance(ref['doi'], str):
                        st.markdown(f"**DOI:  🔗** [{ref['doi']}](https://doi.org/{ref['doi']})")
        
        # Show load more button if there are more references
        remaining_refs = total_refs - st.session_state.refs_per_page[year]
        if remaining_refs > 0:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"📥 Load More ({remaining_refs} references remaining for {year})",
                    key=f"load_more_{year}"
                ):
                    st.session_state.refs_per_page[year] += 10
                    st.experimental_rerun()
                
                # Add reset button if showing more than initial 10
                if st.session_state.refs_per_page[year] > 10:
                    if st.button("🔄 Reset View", key=f"reset_view_{year}"):
                        st.session_state.refs_per_page[year] = 10
                        st.experimental_rerun()

# Add download button for filtered references
if len(filtered_df) > 0:
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📥Export References")
    
    # Prepare download data
    download_df = filtered_df[[
        'title', 'author', 'year', 'journal', 'citations', 
        'doi', 'countries', 'author_keywords'
    ]]
    
    csv = download_df.to_csv(index=False)
    st.sidebar.download_button(
        label="📥 Download as CSV",
        data=csv,
        file_name="filtered_references.csv",
        mime="text/csv",
        key="download_csv"
    )