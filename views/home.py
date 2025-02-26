import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud
from utils.data_processor import DataProcessor
from utils.text_analysis import TextAnalyzer
from utils.visualizations import Visualizer
import plotly.express as px
import plotly.graph_objects as go
from io import BytesIO
import numpy as np

# Initialize session state for data processing
if 'data_processor' not in st.session_state:
    st.session_state.data_processor = DataProcessor('attached_assets/df.csv')
    st.session_state.text_analyzer = TextAnalyzer(st.session_state.data_processor.df)
    st.session_state.visualizer = Visualizer()

# Add custom CSS
st.markdown("""
<style>
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    .stMetric {
        min-height: auto !important;
    }
    .streamlit-expanderHeader {
        word-break: break-word;
    }
    .js-plotly-plot {
        padding: 0 !important;
    }
    .summary-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
    }
    .tab-subheader {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    @media (max-width: 768px) {
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
        [data-testid="column"] {
            width: 100% !important;
            margin-bottom: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

# Initialize filter states if not already present
if 'search_query' not in st.session_state:
    st.session_state.search_query = ""
if 'year_range' not in st.session_state:
    years = st.session_state.data_processor.df['year'].dropna().astype(int)
    st.session_state.year_range = (int(years.min()), int(years.max()))
if 'selected_countries' not in st.session_state:
    st.session_state.selected_countries = []
if 'selected_journals' not in st.session_state:
    st.session_state.selected_journals = []
if 'active_tab' not in st.session_state:
    st.session_state.active_tab = 0

# Sidebar filters with improved mobile layout
with st.sidebar:
    st.title("Filters 🔍")

    # Search bar
    st.session_state.search_query = st.text_input(
        "Search Titles",
        value=st.session_state.search_query,
        key="sidebar_search"
    )

    # Year range slider
    years = st.session_state.data_processor.df['year'].dropna().astype(int)
    st.session_state.year_range = st.slider(
        "Publication Years",
        min_value=int(years.min()),
        max_value=int(years.max()),
        value=st.session_state.year_range,
        key="sidebar_year_range"
    )

    # Country selection
    countries = st.session_state.data_processor.df['countries'].value_counts().head(20).index
    st.session_state.selected_countries = st.multiselect(
        "Select Countries",
        options=countries,
        default=st.session_state.selected_countries,
        key="sidebar_countries"
    )

    # Journal selection
    journals = st.session_state.data_processor.df['journal'].value_counts().head(20).index
    st.session_state.selected_journals = st.multiselect(
        "Select Journals",
        options=journals,
        default=st.session_state.selected_journals,
        key="sidebar_journals"
    )
    
    # Reset filters button
    if st.button("Reset All Filters"):
        st.session_state.search_query = ""
        st.session_state.year_range = (int(years.min()), int(years.max()))
        st.session_state.selected_countries = []
        st.session_state.selected_journals = []
        st.experimental_rerun()

# Apply filters to create filtered dataframe
df = st.session_state.data_processor.df.copy()
if st.session_state.search_query:
    df = df[df['title'].str.contains(st.session_state.search_query, case=False, na=False)]
df = df[
    (df['year'] >= st.session_state.year_range[0]) &
    (df['year'] <= st.session_state.year_range[1])
]
if st.session_state.selected_countries:
    df = df[df['countries'].isin(st.session_state.selected_countries)]
if st.session_state.selected_journals:
    df = df[df['journal'].isin(st.session_state.selected_journals)]

# Main content
st.title("Maternal Anemia Research Dashboard  🔬📊")

# Dashboard Summary Card Function
def show_dashboard_summary(df):
    """Display a summary card at the top of the dashboard"""
    
    # Create a card-like container with background color
    st.markdown('<div class="summary-card">', unsafe_allow_html=True)
    
    # Create a layout with columns
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown("### Maternal Anemia Research Overview")
        
        # Generate dynamic text based on data
        if 'year' in df.columns:
            start_year = int(df['year'].min())
            end_year = int(df['year'].max())
        else:
            start_year = "N/A"
            end_year = "N/A"
            
        total_papers = len(df)
        
        # For recent papers, consider the latest 3 years if we have year data
        if 'year' in df.columns:
            recent_papers = len(df[df['year'] >= end_year - 2])  
        else:
            recent_papers = "N/A"
        
        st.markdown(f"""
        This dashboard presents an analysis of **{total_papers}** research publications on maternal anemia 
        spanning from **{start_year}** to **{end_year}**. In the past three years, there have been 
        **{recent_papers}** new publications in this field.
        """)
    
    with col2:
        # Show a small trend graph if year data is available
        if 'year' in df.columns:
            year_counts = df['year'].value_counts().sort_index()
            recent_years = sorted(year_counts.index)[-10:]  # Last 10 years
            recent_counts = [year_counts.get(year, 0) for year in recent_years]
            
            # Create a mini trend chart
            fig = px.line(
                x=recent_years, 
                y=recent_counts,
                labels={'x': 'Year', 'y': 'Publications'},
                height=100
            )
            fig.update_layout(
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                xaxis=dict(showticklabels=False, showgrid=False),
                yaxis=dict(showticklabels=False, showgrid=False)
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("*Publications trend (last 10 years)*")
    
    with col3:
        # Show the current filter state
        st.markdown("**Current Filters:**")
        
        if st.session_state.search_query:
            st.markdown(f"🔍 Search: `{st.session_state.search_query}`")
        
        if 'year' in df.columns:
            st.markdown(f"📅 Years: {st.session_state.year_range[0]} - {st.session_state.year_range[1]}")
        
        if st.session_state.selected_countries:
            country_str = ", ".join(st.session_state.selected_countries[:2])
            if len(st.session_state.selected_countries) > 2:
                country_str += f" + {len(st.session_state.selected_countries) - 2} more"
            st.markdown(f"🌎 Countries: {country_str}")
        
        if st.session_state.selected_journals:
            journal_str = ", ".join(st.session_state.selected_journals[:2])
            if len(st.session_state.selected_journals) > 2:
                journal_str += f" + {len(st.session_state.selected_journals) - 2} more"
            st.markdown(f"📚 Journals: {journal_str}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# Research Focus Area Function
def show_research_focus(df):
    """Display research focus area analysis section"""
    st.markdown('<div class="tab-subheader">Research Focus Areas 🔍</div>', unsafe_allow_html=True)
    
    # Create two columns
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Get top research areas
        if 'research_areas' in df.columns:
            # Extract and count research areas
            all_areas = []
            for areas in df['research_areas'].dropna():
                if ';' in str(areas):
                    areas_list = [area.strip() for area in str(areas).split(';') if area.strip()]
                else:
                    areas_list = [areas.strip()]
                all_areas.extend(areas_list)
            
            research_areas = pd.Series(all_areas).value_counts().head(15)
            
            # Plot research areas
            fig = px.bar(
                research_areas,
                orientation='h',
                title="Top Research Focus Areas",
                labels={'index': 'Research Area', 'value': 'Number of Publications'},
                color=research_areas.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                showlegend=False,
                height=500,
                margin=dict(l=10, r=10, t=40, b=20),
                title_x=0.5,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Research area data not available in the dataset.")
    
    with col2:
        # Create word cloud of research areas or keywords
        if 'research_areas' in df.columns or 'keywords' in df.columns:
            # Get text for word cloud
            if 'research_areas' in df.columns:
                text = " ".join(df['research_areas'].dropna().astype(str).tolist())
            else:
                text = " ".join(df['keywords'].dropna().astype(str).tolist())
            
            # Create word cloud
            wc = WordCloud(
                width=800,
                height=400,
                background_color='white',
                max_words=100,
                colormap='viridis',
                max_font_size=80,
                min_font_size=10
            ).generate(text)
            
            # Display word cloud
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.imshow(wc, interpolation='bilinear')
            ax.axis("off")
            plt.tight_layout(pad=0)
            st.pyplot(fig)
        else:
            st.info("Research area or keyword data not available for visualization.")

# Publication Impact Analysis Function
def show_impact_analysis(df):
    """Display publication impact analysis"""
    st.markdown('<div class="tab-subheader">Publication Impact Analysis 📊</div>', unsafe_allow_html=True)
    
    # Create tabs for different impact metrics
    impact_tabs = st.tabs(["Citation Analysis", "Journal Impact", "Yearly Impact"])
    
    with impact_tabs[0]:
        # Citation distribution
        if 'citations' in df.columns:
            # Create citation buckets
            citation_bins = [0, 10, 50, 100, 500, 1000, float('inf')]
            labels = ['0-9', '10-49', '50-99', '100-499', '500-999', '1000+']
            
            citation_counts = pd.cut(df['citations'], bins=citation_bins, labels=labels)
            citation_dist = citation_counts.value_counts().sort_index()
            
            # Plot citation distribution
            fig = px.bar(
                citation_dist,
                title="Citation Distribution",
                labels={'index': 'Citation Range', 'value': 'Number of Publications'},
                color=citation_dist.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=10, r=10, t=40, b=20),
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Most cited papers
            st.subheader("Most Cited Publications")
            if 'author_list' in df.columns:
                top_cited = df.nlargest(5, 'citations')[['title', 'author_list', 'year', 'citations']]
            else:
                top_cited = df.nlargest(5, 'citations')[['title', 'year', 'citations']]
            st.dataframe(top_cited, height=200)
        else:
            st.info("Citation data not available in the dataset.")
    
    with impact_tabs[1]:
        # Journal impact
        if 'journal' in df.columns:
            # Get publication count by journal
            journal_counts = df['journal'].value_counts().head(10)
            
            # Get average citations by journal if citation data is available
            if 'citations' in df.columns:
                journal_citations = df.groupby('journal')['citations'].mean().sort_values(ascending=False).head(10)
                
                # Plot journals by average citations
                fig = px.bar(
                    journal_citations,
                    title="Top Journals by Average Citations",
                    labels={'index': 'Journal', 'value': 'Average Citations per Paper'},
                    color=journal_citations.values,
                    color_continuous_scale='Viridis'
                )
                fig.update_layout(
                    showlegend=False,
                    height=400,
                    margin=dict(l=10, r=10, t=40, b=20),
                    title_x=0.5,
                    xaxis={'tickangle': 45}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            # Plot journals by publication count
            fig = px.bar(
                journal_counts,
                title="Top Journals by Publication Count",
                labels={'index': 'Journal', 'value': 'Number of Publications'},
                color=journal_counts.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=10, r=10, t=40, b=20),
                title_x=0.5,
                xaxis={'tickangle': 45}
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Journal data not available in the dataset.")
    
    with impact_tabs[2]:
        # Yearly impact
        if 'year' in df.columns and 'citations' in df.columns:
            # Calculate average citations by year
            yearly_avg_citations = df.groupby('year')['citations'].mean()
            
            # Plot yearly average citations
            fig = px.line(
                yearly_avg_citations,
                title="Average Citations per Publication by Year",
                labels={'index': 'Year', 'value': 'Average Citations'},
                markers=True
            )
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=40, b=20),
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Calculate total citations by year
            yearly_total_citations = df.groupby('year')['citations'].sum()
            
            # Plot yearly total citations
            fig = px.bar(
                yearly_total_citations,
                title="Total Citations by Publication Year",
                labels={'index': 'Year', 'value': 'Total Citations'},
                color=yearly_total_citations.values,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                showlegend=False,
                height=400,
                margin=dict(l=10, r=10, t=40, b=20),
                title_x=0.5
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Year and citation data not available for the dataset.")

# Timeline View Function
def show_timeline(df):
    """Display interactive timeline of publications"""
    st.markdown('<div class="tab-subheader">Research Timeline 📅</div>', unsafe_allow_html=True)
    
    if 'year' in df.columns:
        # Create year filter with a range slider
        min_year = int(df['year'].min())
        max_year = int(df['year'].max())
        
        selected_years = st.slider(
            "Select Year Range for Timeline",
            min_value=min_year,
            max_value=max_year,
            value=(min_year, max_year),
            key="timeline_year_range"
        )
        
        # Filter data by selected years
        timeline_df = df[(df['year'] >= selected_years[0]) & (df['year'] <= selected_years[1])]
        
        # Group by year and get publication counts
        yearly_counts = timeline_df.groupby('year').size().reset_index(name='count')
        
        # Create timeline visualization
        fig = px.line(
            yearly_counts,
            x='year',
            y='count',
            title="Publications by Year",
            labels={'year': 'Year', 'count': 'Number of Publications'},
            markers=True
        )
        
        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=40, b=20),
            title_x=0.5
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show publication list by year (interactive)
        st.subheader("Publications by Year")
        
        # Allow user to select a specific year
        selected_year = st.selectbox(
            "Select a Year to View Publications",
            options=sorted(timeline_df['year'].unique(), reverse=True)
        )
        
        # Show publications for selected year
        year_pubs = timeline_df[timeline_df['year'] == selected_year]
        
        if not year_pubs.empty:
            # Display publications sorted by citations (if available)
            if 'citations' in year_pubs.columns:
                year_pubs = year_pubs.sort_values('citations', ascending=False)
            
            for i, (_, row) in enumerate(year_pubs.iterrows()):
                # Limit to first 15 publications for performance
                if i >= 15:
                    st.info(f"Showing 15 of {len(year_pubs)} publications. Refine your filters to see others.")
                    break
                    
                with st.expander(f"{row['title']}"):
                    # Build publication details
                    details = ""
                    if 'author_list' in row and isinstance(row['author_list'], list):
                        details += f"**Authors:** {', '.join(row['author_list'])}\n\n"
                    elif 'authors' in row:
                        details += f"**Authors:** {row['authors']}\n\n"
                    
                    if 'journal' in row:
                        details += f"**Journal:** {row['journal']}\n\n"
                    
                    if 'citations' in row:
                        details += f"**Citations:** {row['citations']}\n\n"
                    
                    if 'abstract' in row and pd.notna(row['abstract']):
                        details += f"**Abstract:** {row['abstract']}\n\n"
                    
                    st.markdown(details)
        else:
            st.info(f"No publications found for {selected_year}.")
    else:
        st.info("Year data not available for timeline visualization.")

# Collaboration Network Preview Function
def show_collaboration_preview(df):
    """Display a preview of collaboration networks"""
    st.markdown('<div class="tab-subheader">Collaboration Networks Preview 🌐</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Author Collaboration")
        
        # Create a simple preview of author collaboration
        if 'author_list' in df.columns:
            # Count co-authorships
            author_pairs = []
            for authors in df['author_list'].dropna():
                if isinstance(authors, list) and len(authors) > 1:
                    # Get all possible pairs of authors
                    for i in range(len(authors)):
                        for j in range(i+1, len(authors)):
                            author_pairs.append((authors[i], authors[j]))
            
            # Count frequencies of each pair
            from collections import Counter
            pair_counts = Counter(author_pairs)
            
            # Get top collaborating pairs
            top_pairs = pd.DataFrame(pair_counts.most_common(10), 
                                    columns=['Author Pair', 'Collaborations'])
            top_pairs['Author Pair'] = top_pairs['Author Pair'].apply(
                lambda x: f"{x[0]} & {x[1]}"
            )
            
            # Display top collaborating pairs
            st.write("Top Collaborating Author Pairs:")
            st.dataframe(top_pairs, height=300)
        else:
            st.info("Author data not available for collaboration analysis.")
        
        st.markdown("[View Full Network in Author Co-authorship Network Page →]()")
    
    with col2:
        st.markdown("#### Institution Collaboration")
        
        # Create a simple preview of institution collaboration
        if 'affiliation_list' in df.columns:
            # Count collaborations between institutions
            institution_pairs = []
            for institutions in df['affiliation_list'].dropna():
                if isinstance(institutions, list) and len(institutions) > 1:
                    # Get all possible pairs of institutions
                    for i in range(len(institutions)):
                        for j in range(i+1, len(institutions)):
                            institution_pairs.append((institutions[i], institutions[j]))
            
            # Count frequencies of each pair
            from collections import Counter
            pair_counts = Counter(institution_pairs)
            
            # Get top collaborating pairs
            top_pairs = pd.DataFrame(pair_counts.most_common(10), 
                                    columns=['Institution Pair', 'Collaborations'])
            top_pairs['Institution Pair'] = top_pairs['Institution Pair'].apply(
                lambda x: f"{x[0]} & {x[1]}"
            )
            
            # Display top collaborating pairs
            st.write("Top Collaborating Institution Pairs:")
            st.dataframe(top_pairs, height=300)
        else:
            st.info("Institution data not available for collaboration analysis.")
        
        st.markdown("[View Full Network in Organization Co-authorship Network Page →]()")

# Data Download Function
def show_data_download(df):
    """Provide options to download filtered data"""
    st.markdown('<div class="tab-subheader">Download Data 📥</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Download Current View")
        st.write("Download the currently filtered dataset as CSV or Excel.")
        
        format_option = st.radio(
            "Select Format",
            options=["CSV", "Excel"],
            horizontal=True
        )
        
        if format_option == "CSV":
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="maternal_anemia_research_data.csv",
                mime="text/csv"
            )
        else:
            # Use BytesIO to handle Excel files
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            
            excel_data = buffer.getvalue()
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name="maternal_anemia_research_data.xlsx",
                mime="application/vnd.ms-excel"
            )
    
    with col2:
        st.markdown("#### Download Custom Selection")
        st.write("Select specific columns to include in your download.")
        
        # Let user select columns
        available_columns = df.columns.tolist()
        selected_columns = st.multiselect(
            "Select Columns",
            options=available_columns,
            default=available_columns[:5]  # Select first 5 columns by default
        )
        
        if selected_columns:
            custom_df = df[selected_columns]
            
            format_option = st.radio(
                "Select Format",
                options=["CSV", "Excel"],
                horizontal=True,
                key="custom_format"
            )
            
            if format_option == "CSV":
                csv = custom_df.to_csv(index=False)
                st.download_button(
                    label="Download Custom CSV",
                    data=csv,
                    file_name="maternal_anemia_research_custom.csv",
                    mime="text/csv"
                )
            else:
                # Use BytesIO to handle Excel files
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    custom_df.to_excel(writer, sheet_name='Data', index=False)
                
                excel_data = buffer.getvalue()
                st.download_button(
                    label="Download Custom Excel",
                    data=excel_data,
                    file_name="maternal_anemia_research_custom.xlsx",
                    mime="application/vnd.ms-excel"
                )
        else:
            st.warning("Please select at least one column.")

# Show dashboard summary at the top
show_dashboard_summary(df)

# Tab-based organization for the main content
main_tabs = st.tabs([
    "Overview",
    "Research Areas",
    "Impact Analysis", 
    "Geography",
    "Timeline", 
    "Top Contributors",
    "Download Data"
])

# Overview Tab
with main_tabs[0]:
    # Key metrics
    st.markdown("### Key Metrics 📈")
    metrics_container = st.container()
    with metrics_container:
        # Use custom CSS classes for better mobile layout
        col1, col2, col3 = st.columns(3)
        kpi_metrics = st.session_state.data_processor.get_kpi_metrics(df)  # Apply filter to KPI calculation

        with col1:
            st.metric("Total Articles", kpi_metrics['total_articles'])
            st.metric("Total Authors", kpi_metrics['total_authors'])
        with col2:
            st.metric("Total Institutions", kpi_metrics['total_institutions'])
            st.metric("Total Countries", kpi_metrics['total_countries'])
        with col3:
            st.metric("Total Citations", kpi_metrics['total_citations'])

    # Research trends
    st.subheader("Research Trends 📋")
    yearly_pubs, yearly_citations = st.session_state.data_processor.get_yearly_trends(df)  # Apply filter to trend calculation
    trends_fig = st.session_state.visualizer.create_yearly_trends_plot(yearly_pubs, yearly_citations)
    st.plotly_chart(trends_fig, use_container_width=True)

    # # Top contributors
    # st.subheader("Top Contributors 👥")
    # col1, col2, col3 = st.columns(3)

    # with col1:
    #     # Process authors data
    #     top_authors = df['author_list'].explode().value_counts().head(10).sort_values(ascending=True)
    #     fig = px.bar(
    #         top_authors, 
    #         orientation='h',
    #         title="Top 10 Authors",
    #         labels={'index': 'Author', 'value': 'Number of Publications'}
    #     )
    #     fig.update_layout(
    #         showlegend=False, 
    #         height=400,
    #         margin=dict(l=10, r=10, t=40, b=20),
    #         title_x=0.5
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

    # with col2:
    #     # Process countries data
    #     countries = df['countries'].value_counts().head(10).sort_values(ascending=True)
    #     fig = px.bar(
    #         countries, 
    #         orientation='h',
    #         title="Top 10 Countries",
    #         labels={'index': 'Country', 'value': 'Number of Publications'}
    #     )
    #     fig.update_layout(
    #         showlegend=False, 
    #         height=400,
    #         margin=dict(l=10, r=10, t=40, b=20),
    #         title_x=0.5
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

    # with col3:
    #     # Process institutions data
    #     institutions = df['affiliation_list'].explode().value_counts().head(10).sort_values(ascending=True)
    #     fig = px.bar(
    #         institutions, 
    #         orientation='h',
    #         title="Top 10 Institutions",
    #         labels={'index': 'Institution', 'value': 'Number of Publications'}
    #     )
    #     fig.update_layout(
    #         showlegend=False, 
    #         height=400,
    #         margin=dict(l=10, r=10, t=40, b=20),
    #         title_x=0.5
    #     )
    #     st.plotly_chart(fig, use_container_width=True)

# Research Areas Tab
with main_tabs[1]:
    show_research_focus(df)

# Impact Analysis Tab
with main_tabs[2]:
    show_impact_analysis(df)

# Geography Tab
with main_tabs[3]:
    st.markdown('<div class="tab-subheader">Geographical Distribution 🗺️</div>', unsafe_allow_html=True)
    country_counts = df['countries'].value_counts()
    
    # Use improved world map with discrete colors
    world_map = st.session_state.visualizer.create_world_map(country_counts, discrete_colors=True)
    # st.plotly_chart(world_map,
# Geography Tab (continued)
    st.plotly_chart(world_map, use_container_width=True)
    
    # Add country-specific analysis
    st.subheader("Country-Specific Analysis")
    
    # Allow user to select a specific country to analyze
    if len(country_counts) > 0:
        selected_country = st.selectbox(
            "Select a Country to Analyze",
            options=sorted(country_counts.index)
        )
        
        # Filter data for selected country
        country_data = df[df['countries'] == selected_country]
        
        # Display country statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Publications", len(country_data))
        
        with col2:
            if 'year' in country_data.columns:
                first_year = int(country_data['year'].min())
                st.metric("First Publication", first_year)
        
        with col3:
            if 'citations' in country_data.columns:
                total_citations = country_data['citations'].sum()
                st.metric("Total Citations", total_citations)
        
        # Show publications trend for this country if year data is available
        if 'year' in country_data.columns:
            # Group by year
            country_yearly = country_data.groupby('year').size().reset_index(name='count')
            
            # Create line chart
            fig = px.line(
                country_yearly,
                x='year',
                y='count',
                title=f"Publication Trend for {selected_country}",
                labels={'year': 'Year', 'count': 'Number of Publications'},
                markers=True
            )
            
            fig.update_layout(
                height=400,
                margin=dict(l=10, r=10, t=40, b=20),
                title_x=0.5
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Show top institutions from this country
        if 'affiliation_list' in country_data.columns:
            st.subheader(f"Top Institutions in {selected_country}")
            institutions = country_data['affiliation_list'].explode().value_counts().head(10)
            
            if len(institutions) > 0:
                fig = px.bar(
                    institutions,
                    title=f"Top Institutions in {selected_country}",
                    labels={'index': 'Institution', 'value': 'Number of Publications'},
                    color=institutions.values,
                    color_continuous_scale='Viridis'
                )
                
                fig.update_layout(
                    height=400,
                    margin=dict(l=10, r=10, t=40, b=20),
                    title_x=0.5,
                    xaxis={'tickangle': 45}
                )
                
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info(f"No institution data available for {selected_country}.")
    else:
        st.info("No country data available in the filtered dataset.")

# Timeline Tab
with main_tabs[4]:
    show_timeline(df)

# Networks Tab
with main_tabs[5]:
    # st.markdown('<div class="tab-subheader">Research Collaboration Networks 🔬</div>', unsafe_allow_html=True)
    
    # Author Collaboration Section
    # st.subheader("Author Collaboration Analysis 👥")
    
    if 'author_list' in df.columns:
        # Count co-authorships using a more efficient approach
        author_pairs = []
        collaboration_strengths = {}
        
        for _, row in df.iterrows():
            if 'author_list' in row and isinstance(row['author_list'], list) and len(row['author_list']) > 1:
                authors = row['author_list']
                for i in range(len(authors)):
                    for j in range(i+1, len(authors)):
                        pair = (min(authors[i], authors[j]), max(authors[i], authors[j]))
                        author_pairs.append(pair)
                        
                        # Track collaboration strength
                        if pair not in collaboration_strengths:
                            collaboration_strengths[pair] = 0
                        collaboration_strengths[pair] += 1
        
        # Count frequencies of each pair
        from collections import Counter
        pair_counts = Counter(author_pairs)
        
        # Show top authors by publication count
        st.markdown("#### Top Authors by Publication Count")
        
        top_authors = df['author_list'].explode().value_counts().head(10)
        
        fig1 = px.bar(
            top_authors,
            orientation='h',
            title="Top 10 Authors by Publication Count",
            labels={'index': 'Author', 'value': 'Number of Publications'},
            color=top_authors.values,
            color_continuous_scale='Blues'
        )
        
        fig1.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=20),
            title_x=0.5,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig1, use_container_width=True)
        
        # Show top collaborating pairs
        st.markdown("#### Top Collaborating Author Pairs")
        
        top_pairs = pd.DataFrame(pair_counts.most_common(10), 
                                 columns=['Author Pair', 'Collaborations'])
        top_pairs['Author Pair'] = top_pairs['Author Pair'].apply(
            lambda x: f"{x[0]} & {x[1]}"
        )
        
        fig2 = px.bar(
            top_pairs,
            x='Collaborations',
            y='Author Pair',
            orientation='h',
            title="Top 10 Collaborating Author Pairs",
            color='Collaborations',
            color_continuous_scale='Reds'
        )
        
        fig2.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=20),
            title_x=0.5
        )
        
        st.plotly_chart(fig2, use_container_width=True)
        
    #     # Link to full network visualization
    #     st.markdown("[🔗 View Full Author Co-authorship Network]()")
    # else:
    #     st.info("Author data not available for collaboration analysis.")
    
    # Institution Collaboration Section
    st.markdown("---")
    st.subheader("Institution Collaboration Analysis 🏛️")
    
    if 'affiliation_list' in df.columns:
        # Show top institutions by publication count
        st.markdown("#### Top Institutions by Publication Count")
        
        top_institutions = df['affiliation_list'].explode().value_counts().head(10)
        
        fig3 = px.bar(
            top_institutions,
            orientation='h',
            title="Top 10 Institutions by Publication Count",
            labels={'index': 'Institution', 'value': 'Number of Publications'},
            color=top_institutions.values,
            color_continuous_scale='Greens'
        )
        
        fig3.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=20),
            title_x=0.5,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig3, use_container_width=True)
        
        # Count collaborations between institutions
        institution_pairs = []
        
        for _, row in df.iterrows():
            if 'affiliation_list' in row and isinstance(row['affiliation_list'], list) and len(row['affiliation_list']) > 1:
                institutions = row['affiliation_list']
                for i in range(len(institutions)):
                    for j in range(i+1, len(institutions)):
                        pair = (min(institutions[i], institutions[j]), max(institutions[i], institutions[j]))
                        institution_pairs.append(pair)
        
        # Count frequencies of each pair
        from collections import Counter
        institution_pair_counts = Counter(institution_pairs)
        
        # Show top collaborating institution pairs
        st.markdown("#### Top Collaborating Institution Pairs")
        
        top_inst_pairs = pd.DataFrame(institution_pair_counts.most_common(10), 
                                    columns=['Institution Pair', 'Collaborations'])
        top_inst_pairs['Institution Pair'] = top_inst_pairs['Institution Pair'].apply(
            lambda x: f"{x[0]} & {x[1]}"
        )
        
        fig4 = px.bar(
            top_inst_pairs,
            x='Collaborations',
            y='Institution Pair',
            orientation='h',
            title="Top 10 Collaborating Institution Pairs",
            color='Collaborations',
            color_continuous_scale='Purples'
        )
        
        fig4.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=20),
            title_x=0.5
        )
        
        st.plotly_chart(fig4, use_container_width=True)
        
    #     # Link to full network visualization
    #     st.markdown("[🔗 View Full Organization Co-authorship Network]()")
    # else:
    #     st.info("Institution data not available for collaboration analysis.")
    
    # Country Collaboration Section
    st.markdown("---")
    st.subheader("Country Collaboration Analysis 🌎")
    
    if 'countries' in df.columns:
        # Show top countries by publication count
        st.markdown("#### Top Countries by Publication Count")
        
        top_countries = df['countries'].value_counts().head(10)
        
        fig5 = px.bar(
            top_countries,
            orientation='h',
            title="Top 10 Countries by Publication Count",
            labels={'index': 'Country', 'value': 'Number of Publications'},
            color=top_countries.values,
            color_continuous_scale='Oranges'
        )
        
        fig5.update_layout(
            showlegend=False,
            height=400,
            margin=dict(l=10, r=10, t=40, b=20),
            title_x=0.5,
            yaxis={'categoryorder': 'total ascending'}
        )
        
        st.plotly_chart(fig5, use_container_width=True)
        
    #     # Link to full network visualization
    #     st.markdown("[🔗 View Full Country Citation Network]()")
    # else:
    #     st.info("Country data not available for collaboration analysis.")
    




# Download Data Tab
with main_tabs[6]:
    show_data_download(df)