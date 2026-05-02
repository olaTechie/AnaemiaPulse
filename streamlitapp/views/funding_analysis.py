import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from wordcloud import WordCloud
import re
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import os
from io import BytesIO
import base64

# Helper functions - DEFINED FIRST
def extract_funding_sources(df):
    """Extract individual funding sources from the funding_details column"""
    all_sources = []
    
    for details in df['funding_details'].dropna():
        # Split by semicolon to get individual sources
        sources = [source.strip() for source in str(details).split(';') if source.strip()]
        all_sources.extend(sources)
    
    return all_sources

def clean_funding_sources(sources, normalize_names=True, handle_abbreviations=True):
    """Clean and normalize funding sources with advanced processing options"""
    # Basic cleaning
    cleaned = []
    for source in sources:
        # Remove "Funding Source:" text that appears in some entries
        source = re.sub(r'Funding Source:\s*', '', source)
        
        # Remove grant numbers in brackets
        source = re.sub(r'\[.*?\]', '', source)
        
        # Remove trailing punctuation and whitespace
        source = source.strip().rstrip('.,;:')
        
        if source:  # Only add non-empty sources
            cleaned.append(source)
    
    # Apply advanced processing options
    if handle_abbreviations:
        cleaned = detect_abbreviations(cleaned)
        
    if normalize_names:
        cleaned = normalize_funding_sources(cleaned)
    
    return cleaned

def normalize_funding_sources(sources):
    """Normalize known organization names for consistency"""
    normalized = []
    
    for source in sources:
        lower_source = source.lower()
        
        # More comprehensive normalization for Gates Foundation variations
        if any(term in lower_source for term in ["gates", "bill", "melinda"]):
            source = "Bill & Melinda Gates Foundation"
        elif "wellcome trust" in lower_source or lower_source == "wellcome":
            source = "Wellcome Trust"
        elif "nih" in lower_source and "nichd" in lower_source:
            source = "NICHD NIH"
        elif "vifor" in lower_source:
            source = "Vifor Pharma"
        elif "national institutes of health research" in lower_source or "nihr" in lower_source:
            source = "National Institutes of Health Research (NIHR)"
        
        normalized.append(source)
    
    return normalized

def detect_abbreviations(sources):
    """Detect and normalize abbreviations in parentheses"""
    # Regex to find patterns like "Organization Name (ON)"
    abbrev_pattern = re.compile(r'(.*?)\s+\(([A-Z0-9]+)\)$')
    
    # Map of abbreviations to full names
    abbrev_map = {}
    
    # Find all abbreviations
    for source in sources:
        match = abbrev_pattern.match(source)
        if match:
            full_name, abbrev = match.groups()
            # Store only if abbreviation seems valid (all uppercase, reasonable length)
            if abbrev.isupper() and 2 <= len(abbrev) <= 10:
                abbrev_map[abbrev] = full_name.strip()
    
    # Normalize the sources
    normalized = []
    for source in sources:
        # Check if this source is just an abbreviation
        if source in abbrev_map:
            # Replace with full name
            normalized.append(abbrev_map[source])
        else:
            # Keep as is
            normalized.append(source)
    
    return normalized

def get_top_sources(sources, n=20):
    """Get the top n funding sources by frequency"""
    source_counts = Counter(sources)
    return source_counts.most_common(n)

def create_wordcloud(sources, max_words=100, colormap='viridis', font_path=None):
    """Create a word cloud from funding sources with proper handling of multi-word names"""
    # Count the frequency of each funding source
    source_counts = Counter(sources)
    
    # Create a dictionary where keys are sources and values are frequencies
    # This ensures multi-word organizations stay together
    frequencies = {source: count for source, count in source_counts.items()}
    
    # Setup wordcloud parameters
    wordcloud_params = {
        'width': 1000,
        'height': 600,
        'background_color': 'white',
        'colormap': colormap,
        'max_words': max_words,
        'prefer_horizontal': 0.9,
        'relative_scaling': 0.5,
        'min_font_size': 10,
        'max_font_size': 150,
        'random_state': 42
    }
    
    # Add custom font if available
    if font_path and os.path.exists(font_path):
        wordcloud_params['font_path'] = font_path
    
    # Generate the word cloud
    wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(frequencies)
    
    return wordcloud

def get_wordcloud_download_link(wordcloud, filename="wordcloud.png"):
    """Generate a download link for the wordcloud image"""
    # Save wordcloud to a BytesIO object
    img = BytesIO()
    wordcloud.to_image().save(img, format='PNG')
    img.seek(0)
    
    # Create a download link
    b64 = base64.b64encode(img.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">Download Word Cloud Image</a>'
    return href

# Check if data processor is initialized
if 'data_processor' not in st.session_state:
    st.error("⚠️ Data processor not initialized. Please go to the Overview page first.")
    st.stop()

# Add custom CSS
st.markdown("""
<style>
    .sub-header {
        font-size: 1.8rem;
        color: #0D47A1;
    }
    .chart-container {
        border-radius: 5px;
        border: 1px solid #e0e0e0;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Main title
st.title("💰 Funding Sources Analysis 📊")

# Get data from session state
df = st.session_state.data_processor.df

# Check if funding_details column exists
if 'funding_details' not in df.columns:
    st.error("⚠️ This dataset doesn't contain a 'funding_details' column. Please check your data.")
    st.stop()

# Sidebar for options
st.sidebar.title("⚙️ Options")

# Processing options
st.sidebar.subheader("🔧 Processing Options")
normalize_names = st.sidebar.checkbox("Normalize organization names", value=True, 
                                     help="Standardize common organization names (e.g., Gates Foundation variations)")

handle_abbreviations = st.sidebar.checkbox("Handle abbreviations", value=True, 
                                         help="Detect and standardize organization abbreviations in parentheses")

# Visualization options
st.sidebar.subheader("🎨 Visualization Options")
top_n = st.sidebar.slider("Number of top sources to show", min_value=5, max_value=50, value=20)
max_words = st.sidebar.slider("Max words in word cloud", min_value=20, max_value=200, value=100)
colormap = st.sidebar.selectbox("Color scheme", 
                               options=['viridis', 'plasma', 'inferno', 'magma', 'Blues', 'YlGnBu', 'Spectral'], 
                               index=0)

# Year filter if year column exists
if 'year' in df.columns:
    years = df['year'].dropna().astype(int)
    year_range = st.sidebar.slider(
        "Publication Years",
        min_value=int(years.min()),
        max_value=int(years.max()),
        value=(int(years.min()), int(years.max()))
    )
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
else:
    filtered_df = df

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["📈 Top Funding Contributors", "☁️ Word Cloud", "🔍 Data Analysis"])

# Extract and clean funding sources
raw_sources = extract_funding_sources(filtered_df)

# Apply cleaning and processing options
cleaned_sources = clean_funding_sources(
    raw_sources, 
    normalize_names=normalize_names, 
    handle_abbreviations=handle_abbreviations
)

# Get top N funding sources
top_sources = get_top_sources(cleaned_sources, n=top_n)

# Tab 1: Top Funding Contributors
with tab1:
    st.markdown('<h2 class="sub-header">📈 Top Funding Contributors</h2>', unsafe_allow_html=True)
    
    # Create a DataFrame for the bar chart
    top_df = pd.DataFrame(top_sources, columns=['Source', 'Count'])
    
    # Create an interactive bar chart with Plotly
    fig = px.bar(
        top_df,
        y='Source',
        x='Count',
        orientation='h',
        color='Count',
        color_continuous_scale=px.colors.sequential.Blues,
        height=600
    )
    
    fig.update_layout(
        yaxis={'categoryorder': 'total ascending'},
        xaxis_title="Frequency",
        yaxis_title="Funding Source",
        margin=dict(l=10, r=10, t=10, b=10)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Download button for chart data
    csv = top_df.to_csv(index=False)
    st.download_button(
        label="Download Chart Data as CSV",
        data=csv,
        file_name="top_funding_sources.csv",
        mime="text/csv"
    )

# Tab 2: Word Cloud
with tab2:
    st.markdown('<h2 class="sub-header">☁️ Funding Sources Word Cloud</h2>', unsafe_allow_html=True)
    
    # Generate wordcloud
    font_path = None
    if os.path.exists(os.path.join("attached_assets", "CabinSketch-Bold.ttf")):
        font_path = os.path.join("attached_assets", "CabinSketch-Bold.ttf")
        
    wordcloud = create_wordcloud(cleaned_sources, max_words=max_words, colormap=colormap, font_path=font_path)
    
    # Display the word cloud
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.imshow(wordcloud, interpolation='bilinear')
    ax.axis("off")
    st.pyplot(fig)
    
    # Add download link for the word cloud
    st.markdown(
        get_wordcloud_download_link(wordcloud, "funding_wordcloud.png"),
        unsafe_allow_html=True
    )
    
    # Additional word cloud options
    st.markdown("### Word Cloud Settings")
    if st.button("Regenerate Word Cloud"):
        st.experimental_rerun()
    st.write("Adjust settings in the sidebar for different visualizations")

# Tab 3: Data Analysis
with tab3:
    st.markdown('<h2 class="sub-header">📊 Funding Data Insights</h2>', unsafe_allow_html=True)
    
    # Dataset statistics
    st.subheader("📋 Dataset Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Entries", f"{len(filtered_df)}")
    
    with col2:
        st.metric("Unique Funding Sources", f"{len(set(cleaned_sources))}")
    
    with col3:
        st.metric("Avg. Sources per Entry", f"{len(raw_sources) / len(filtered_df):.2f}")
    
    # Distribution of entries with multiple sources
    st.subheader("📊 Funding Sources Distribution")
    
    # Count number of sources per entry
    sources_per_entry = []
    for details in filtered_df['funding_details'].dropna():
        sources = [source.strip() for source in details.split(';') if source.strip()]
        sources_per_entry.append(len(sources))
    
    # Create histogram of sources per entry
    fig = px.histogram(
        x=sources_per_entry,
        nbins=10,
        labels={'x': 'Number of Funding Sources', 'y': 'Count of Entries'},
        title="Distribution of Entries by Number of Funding Sources",
        color_discrete_sequence=['#1E88E5']
    )
    
    fig.update_layout(bargap=0.1)
    st.plotly_chart(fig, use_container_width=True)
    
    # Funding trends over time if year column exists
    if 'year' in filtered_df.columns:
        st.subheader("📈 Funding Trends Over Time")
        
        # Group funding data by year
        funding_by_year = {}
        for _, row in filtered_df.iterrows():
            if pd.notna(row['year']) and pd.notna(row['funding_details']):
                year = int(row['year'])
                sources = [s.strip() for s in str(row['funding_details']).split(';') if s.strip()]
                
                if year not in funding_by_year:
                    funding_by_year[year] = []
                
                funding_by_year[year].extend(sources)
        
        # Calculate top funding sources by year
        years = sorted(funding_by_year.keys())
        top_sources_by_year = {}
        for year in years:
            counter = Counter(funding_by_year[year])
            top_sources_by_year[year] = counter.most_common(5)
        
        # Create a stacked area chart for top funding sources over time
        top_overall = [source for source, _ in get_top_sources(cleaned_sources, n=5)]
        source_by_year_data = []
        
        for year in years:
            year_counts = Counter(funding_by_year[year])
            for source in top_overall:
                source_by_year_data.append({
                    'Year': year,
                    'Funding Source': source,
                    'Count': year_counts.get(source, 0)
                })
        
        source_year_df = pd.DataFrame(source_by_year_data)
        
        fig = px.area(
            source_year_df,
            x='Year',
            y='Count',
            color='Funding Source',
            title="Top Funding Sources Trends Over Time",
            height=500
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Display the full list of funding sources with counts
    st.subheader("🔍 Complete Funding Sources List")
    
    all_sources_df = pd.DataFrame(Counter(cleaned_sources).most_common(), 
                                 columns=['Source', 'Count'])
    
    # Add search and filter functionality
    search_term = st.text_input("Search for funding sources")
    
    if search_term:
        filtered_df = all_sources_df[all_sources_df['Source'].str.contains(search_term, case=False)]
        st.dataframe(filtered_df, height=400)
    else:
        st.dataframe(all_sources_df, height=400)
    
    # # Download button for all sources
    # csv = all_sources_df.to_csv(index=False)
    # st.download_button(
    #     label="Download All Sources as CSV",
    #     data=csv,
    #     file_name="all_funding_sources.csv",
    #     mime="text/csv"
    # )