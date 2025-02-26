import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import re
from collections import Counter
import os
from io import BytesIO
import base64

# Helper functions - DEFINED FIRST
def extract_research_areas(df):
    """Extract all research areas from the dataframe"""
    all_areas = []
    
    for areas in df['research_areas'].dropna():
        # Check if areas contain semicolons (multiple areas)
        if ';' in str(areas):
            areas_list = [area.strip() for area in str(areas).split(';') if area.strip()]
        elif ',' in str(areas):
            areas_list = [area.strip() for area in str(areas).split(',') if area.strip()]
        else:
            areas_list = [areas.strip()]
        
        all_areas.extend(areas_list)
    
    return all_areas

def normalize_research_areas(areas):
    """Normalize research area names for consistency"""
    normalized = []
    
    for area in areas:
        # Remove any special formatting or extra whitespace
        area = re.sub(r'\s+', ' ', area.strip())
        
        # Fix common variations
        lower_area = area.lower()
        
        if "obstetr" in lower_area and "gynecol" in lower_area:
            area = "Obstetrics & Gynecology"
        elif "internal medicine" in lower_area or "general medicine" in lower_area:
            area = "General & Internal Medicine"
        elif "public health" in lower_area or "environmental health" in lower_area or "occupational health" in lower_area:
            area = "Public, Environmental & Occupational Health"
        elif "nutrition" in lower_area or "diet" in lower_area:
            area = "Nutrition & Dietetics"
        
        normalized.append(area)
    
    return normalized

def get_top_areas(areas, n=20):
    """Get the top n research areas by frequency"""
    area_counts = Counter(areas)
    return area_counts.most_common(n)

def create_wordcloud(areas, max_words=100, font_path=None):
    """Create a word cloud from research areas"""
    # Count the frequency of each area
    area_counts = Counter(areas)
    
    # Create a dictionary for wordcloud
    frequencies = {area: count for area, count in area_counts.items()}
    
    # Generate the word cloud with custom font if available
    wordcloud_params = {
        'width': 800, 
        'height': 400, 
        'background_color': 'white', 
        'colormap': 'viridis',
        'max_words': max_words, 
        'prefer_horizontal': 0.9, 
        'relative_scaling': 0.5,
        'min_font_size': 10, 
        'max_font_size': 150, 
        'random_state': 42
    }
    
    if font_path and os.path.exists(font_path):
        wordcloud_params['font_path'] = font_path
        
    wordcloud = WordCloud(**wordcloud_params).generate_from_frequencies(frequencies)
    
    return wordcloud

def process_areas_by_year(df, normalize=True):
    """Process research areas by year for trend analysis"""
    areas_by_year = {}
    
    for _, row in df.iterrows():
        if 'year' not in row or pd.isna(row['year']):
            continue
            
        year = row['year']
        areas = row['research_areas']
        
        if pd.notna(year) and pd.notna(areas):
            year = int(year)
            
            if year not in areas_by_year:
                areas_by_year[year] = []
            
            # Split areas if they contain semicolons
            if ';' in str(areas):
                areas_list = [area.strip() for area in str(areas).split(';') if area.strip()]
            elif ',' in str(areas):
                areas_list = [area.strip() for area in str(areas).split(',') if area.strip()]
            else:
                areas_list = [areas.strip()]
            
            # Normalize if requested
            if normalize:
                areas_list = normalize_research_areas(areas_list)
            
            areas_by_year[year].extend(areas_list)
    
    return areas_by_year

def create_trend_data(areas_by_year, top_areas):
    """Create data for trend line chart"""
    trend_data = []
    
    # For each year, count occurrences of each top area
    for year, areas in sorted(areas_by_year.items()):
        area_counts = Counter(areas)
        
        for area in top_areas:
            trend_data.append({
                'Year': year,
                'Research Area': area,
                'Count': area_counts.get(area, 0)
            })
    
    return pd.DataFrame(trend_data)

def create_heatmap_data(areas_by_year, top_areas):
    """Create data for heatmap visualization"""
    # Initialize DataFrame with years as columns and research areas as rows
    years = sorted(areas_by_year.keys())
    heatmap_data = pd.DataFrame(index=top_areas, columns=years)
    
    # Fill in the counts
    for year in years:
        area_counts = Counter(areas_by_year[year])
        
        for area in top_areas:
            heatmap_data.loc[area, year] = area_counts.get(area, 0)
    
    # Fill NaN values with 0
    heatmap_data = heatmap_data.fillna(0)
    
    return heatmap_data

def calculate_area_growth(areas_by_year, min_publications=5):
    """Calculate growth rate of research areas"""
    years = sorted(areas_by_year.keys())
    
    if len(years) < 6:  # Need at least 6 years for meaningful comparison
        return pd.DataFrame()
    
    # Split years into recent (last 3 years) and previous (3 years before that)
    recent_years = years[-3:]
    previous_years = years[-6:-3]
    
    # Count occurrences in each period
    recent_counts = Counter()
    for year in recent_years:
        recent_counts.update(areas_by_year[year])
    
    previous_counts = Counter()
    for year in previous_years:
        previous_counts.update(areas_by_year[year])
    
    # Calculate growth rates
    growth_data = []
    
    for area, recent_count in recent_counts.items():
        previous_count = previous_counts.get(area, 0)
        
        # Only include areas with minimum publications
        total_count = recent_count + previous_count
        if total_count >= min_publications:
            # Avoid division by zero
            if previous_count > 0:
                growth_rate = ((recent_count / previous_count) - 1) * 100
            else:
                growth_rate = float('inf')  # Infinite growth if previously zero
            
            growth_data.append({
                'Research Area': area,
                'Growth Rate': growth_rate if growth_rate != float('inf') else 1000,  # Cap infinite growth
                'Recent Count': recent_count,
                'Previous Count': previous_count
            })
    
    # Convert to DataFrame and sort by growth rate
    growth_df = pd.DataFrame(growth_data)
    growth_df = growth_df.sort_values('Growth Rate', ascending=False)
    
    return growth_df

def calculate_area_cooccurrence(df, normalize=True):
    """Calculate co-occurrence of research areas"""
    cooccurrence = {}
    
    for _, row in df.iterrows():
        areas = row['research_areas']
        
        if pd.notna(areas):
            # Split areas
            if ';' in str(areas):
                areas_list = [area.strip() for area in str(areas).split(';') if area.strip()]
            elif ',' in str(areas):
                areas_list = [area.strip() for area in str(areas).split(',') if area.strip()]
            else:
                areas_list = [areas.strip()]
            
            # Skip if only one area
            if len(areas_list) <= 1:
                continue
                
            # Normalize if requested
            if normalize:
                areas_list = normalize_research_areas(areas_list)
            
            # Count co-occurrences of each pair
            for i, area1 in enumerate(areas_list):
                if area1 not in cooccurrence:
                    cooccurrence[area1] = {}
                
                for area2 in areas_list[i+1:]:
                    if area2 not in cooccurrence[area1]:
                        cooccurrence[area1][area2] = 0
                    
                    cooccurrence[area1][area2] += 1
                    
                    # Make sure the reverse mapping exists too
                    if area2 not in cooccurrence:
                        cooccurrence[area2] = {}
                    
                    if area1 not in cooccurrence[area2]:
                        cooccurrence[area2][area1] = 0
                    
                    cooccurrence[area2][area1] += 1
    
    return cooccurrence

def prepare_network_data(cooccurrence, top_areas):
    """Prepare data for network graph visualization"""
    nodes = []
    edges = []
    
    for area1 in top_areas:
        if area1 in cooccurrence:
            # Add node
            nodes.append({
                'id': area1,
                'label': area1,
                'size': 10  # Can be adjusted based on frequency
            })
            
            # Add edges to other top areas
            for area2 in top_areas:
                if area1 != area2 and area2 in cooccurrence[area1]:
                    weight = cooccurrence[area1][area2]
                    
                    if weight > 0:
                        edges.append({
                            'source': area1,
                            'target': area2,
                            'weight': weight
                        })
    
    return {'nodes': nodes, 'edges': edges}

def create_network_graph(network_data):
    """Create a network graph visualization"""
    nodes = network_data['nodes']
    edges = network_data['edges']
    
    # Create node traces
    node_x = []
    node_y = []
    node_text = []
    node_size = []
    
    # Calculate positions using a simple circular layout
    import math
    n = len(nodes)
    radius = 1
    
    for i, node in enumerate(nodes):
        angle = 2 * math.pi * i / n
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        
        node_x.append(x)
        node_y.append(y)
        node_text.append(node['label'])
        node_size.append(node.get('size', 10))
    
    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers+text',
        text=node_text,
        textposition="top center",
        hoverinfo='text',
        marker=dict(
            showscale=True,
            colorscale='YlGnBu',
            size=node_size,
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left'
            ),
            line_width=2
        )
    )
    
    # Create edge traces
    edge_x = []
    edge_y = []
    edge_width = []
    
    for edge in edges:
        source_idx = next(i for i, node in enumerate(nodes) if node['id'] == edge['source'])
        target_idx = next(i for i, node in enumerate(nodes) if node['id'] == edge['target'])
        
        x0, y0 = node_x[source_idx], node_y[source_idx]
        x1, y1 = node_x[target_idx], node_y[target_idx]
        
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_width.append(edge['weight'] / 2)  # Scale edge width based on weight
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1.5, color='#888'),
        hoverinfo='none',
        mode='lines'
    )
    
    # Create the figure
    fig = go.Figure(data=[edge_trace, node_trace],
             layout=go.Layout(
                showlegend=False,
                hovermode='closest',
                margin=dict(b=20,l=5,r=5,t=40),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
             ))
    
    return fig

def create_correlation_matrix(cooccurrence, top_areas):
    """Create correlation matrix for top research areas"""
    import numpy as np
    import pandas as pd
    
    # Initialize matrix
    n = len(top_areas)
    matrix = np.zeros((n, n))
    
    # Fill in co-occurrence counts
    for i, area1 in enumerate(top_areas):
        for j, area2 in enumerate(top_areas):
            if i == j:
                matrix[i][j] = 1.0  # Perfect correlation with self
            elif area1 in cooccurrence and area2 in cooccurrence[area1]:
                # Normalize by frequency
                count1 = sum(cooccurrence[area1].values())
                count2 = sum(cooccurrence[area2].values())
                if count1 > 0 and count2 > 0:
                    matrix[i][j] = cooccurrence[area1][area2] / np.sqrt(count1 * count2)
    
    # Convert to pandas DataFrame for better display
    corr_df = pd.DataFrame(matrix, index=top_areas, columns=top_areas)
    
    return corr_df

def get_cooccurring_areas(filtered_df, selected_area, normalize=True):
    """Get areas that co-occur with a selected research area"""
    cooccur_count = Counter()
    
    for _, row in filtered_df.iterrows():
        areas = row['research_areas']
        
        if pd.notna(areas) and selected_area in str(areas):
            # Split areas
            if ';' in str(areas):
                areas_list = [area.strip() for area in str(areas).split(';') if area.strip()]
            elif ',' in str(areas):
                areas_list = [area.strip() for area in str(areas).split(',') if area.strip()]
            else:
                areas_list = [areas.strip()]
            
            # Normalize if requested
            if normalize:
                areas_list = normalize_research_areas(areas_list)
            
            # Count co-occurring areas (excluding the selected area itself)
            for area in areas_list:
                if area != selected_area:
                    cooccur_count[area] += 1
    
    return cooccur_count.most_common()

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
st.title("🔬 Research Areas Analysis 📈")

# Sidebar for options
st.sidebar.title("⚙️ Options")

# Processing options
st.sidebar.subheader("🔧 Processing Options")
normalize_areas = st.sidebar.checkbox("Normalize research area names", value=True, 
                                     help="Standardize common research area names")

# Visualization options
st.sidebar.subheader("🎨 Visualization Options")
top_n = st.sidebar.slider("Number of top areas to show", min_value=5, max_value=30, value=15)

# Get data from session state
df = st.session_state.data_processor.df

# Check if research_areas column exists
if 'research_areas' not in df.columns:
    st.error("⚠️ This dataset doesn't contain a 'research_areas' column. Please check your data.")
    st.stop()

# Get year range if available
if 'year' in df.columns:
    year_range = st.sidebar.slider(
        "Year range to analyze", 
        min_value=int(df['year'].min()), 
        max_value=int(df['year'].max()),
        value=(int(df['year'].min()), int(df['year'].max()))
    )
    
    # Filter data by year range
    filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]
else:
    filtered_df = df
    year_range = (None, None)

# Create tabs for different views
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Research Area Distribution", 
    "📅 Trends Over Time", 
    "🔄 Interdisciplinary Analysis",
    "🔍 Detailed Analysis"
])

# Extract and process research areas
all_areas = extract_research_areas(filtered_df)
if normalize_areas:
    all_areas = normalize_research_areas(all_areas)

# Get top areas
top_areas = get_top_areas(all_areas, n=top_n)
top_areas_names = [area for area, _ in top_areas]

# Tab 1: Research Area Distribution
with tab1:
    st.markdown('<h2 class="sub-header">📊 Research Area Distribution</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([2, 4])
    
    with col1:

        # Add some key statistics
        st.subheader("📋 Key Statistics")
        st.metric("Total Unique Research Areas", len(set(all_areas)))
        
        if len(top_areas) > 0:
            dominant_area, dominant_count = top_areas[0]
            percentage = (dominant_count / len(all_areas)) * 100
            st.metric("Dominant Research Area", 
                     f"{dominant_area} ({percentage:.1f}%)")
        
        # Create and display a word cloud
        st.subheader("☁️ Research Areas Word Cloud")
        
        # Get custom font path if available
        font_path = None
        if os.path.exists(os.path.join("attached_assets", "CabinSketch-Bold.ttf")):
            font_path = os.path.join("attached_assets", "CabinSketch-Bold.ttf")
        
        wordcloud = create_wordcloud(all_areas, font_path=font_path)
        
        # Display the word cloud
        fig, ax = plt.subplots(figsize=(6, 4))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis("off")
        st.pyplot(fig)


    
    with col2:
        # Create pie chart for top 10 areas

        
        # Create a DataFrame for the bar chart
        top_df = pd.DataFrame(top_areas, columns=['Research Area', 'Count'])
        
        # Create horizontal bar chart
        fig = px.bar(
            top_df,
            y='Research Area',
            x='Count',
            orientation='h',
            color='Count',
            color_continuous_scale='Viridis',
            title=f"Top {top_n} Research Areas ({year_range[0] or 'All'}-{year_range[1] or 'All'})",
            height=600
        )
        
        fig.update_layout(
            yaxis={'categoryorder': 'total ascending'},
            xaxis_title="Number of Publications",
            yaxis_title="Research Area",
            margin=dict(l=10, r=10, t=50, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)

        # pie_df = pd.DataFrame(top_areas[:10], columns=['Research Area', 'Count'])
        
        # fig = px.pie(
        #     pie_df,
        #     values='Count',
        #     names='Research Area',
        #     title=f"Top 10 Research Areas Distribution",
        #     color_discrete_sequence=px.colors.qualitative.Plotly
        # )
        
        # fig.update_traces(textposition='inside', textinfo='percent+label')
        # fig.update_layout(
        #     margin=dict(l=10, r=10, t=50, b=10),
        #     legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5)
        # )
        
        # st.plotly_chart(fig, use_container_width=True)
        
        
# Tab 2: Trends Over Time
with tab2:
    st.markdown('<h2 class="sub-header">📅 Research Trends Over Time</h2>', unsafe_allow_html=True)
    
    if 'year' not in df.columns:
        st.warning("⚠️ This dataset doesn't contain a 'year' column. Temporal analysis is not available.")
    else:
        # Process data for trends
        areas_by_year = process_areas_by_year(filtered_df, normalize=normalize_areas)
        
        # Create line chart showing trends of top areas over time
        trend_data = create_trend_data(areas_by_year, top_areas_names)
        
        # Display trend line chart
        st.subheader("📈 Research Area Trends")
        fig = px.line(
            trend_data, 
            x='Year', 
            y='Count', 
            color='Research Area',
            title='Research Area Trends Over Time',
            height=500
        )
        
        fig.update_layout(
            xaxis_title="Year",
            yaxis_title="Number of Publications",
            legend_title="Research Area",
            hovermode="x unified"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show heatmap of top areas over time
        st.subheader("🔥 Research Area Heatmap by Year")
        
        heatmap_data = create_heatmap_data(areas_by_year, top_areas_names[:15])
        
        fig = px.imshow(
            heatmap_data.values,
            labels=dict(x="Year", y="Research Area", color="Publications"),
            x=heatmap_data.columns,
            y=heatmap_data.index,
            color_continuous_scale="Viridis",
            aspect="auto",
            height=600
        )
        
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10),
            coloraxis_colorbar=dict(title="Publications")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show growth rates of research areas
        st.subheader("🚀 Fastest Growing Research Areas")
        
        growth_data = calculate_area_growth(areas_by_year, min_publications=5)
        
        if not growth_data.empty:
            fig = px.bar(
                growth_data.head(10),
                y='Research Area',
                x='Growth Rate',
                orientation='h',
                color='Growth Rate',
                color_continuous_scale='Viridis',
                title="Top 10 Fastest Growing Research Areas",
                height=400
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Growth Rate (Percentage)",
                yaxis_title="Research Area"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Add explanation
            st.info("Growth rate is calculated by comparing the number of publications in the most recent 3 years to the previous 3 years. Only areas with at least 5 total publications are included.")

# Tab 3: Interdisciplinary Analysis
with tab3:
    st.markdown('<h2 class="sub-header">🔄 Interdisciplinary Research Analysis</h2>', unsafe_allow_html=True)
    
    # Calculate co-occurrence of research areas
    cooccurrence = calculate_area_cooccurrence(filtered_df, normalize=normalize_areas)
    
    # Display network graph of research area connections
    st.subheader("🕸️ Research Area Connections")
    
    # Only include top areas to keep visualization manageable
    if len(cooccurrence) > 0:
        network_data = prepare_network_data(cooccurrence, top_areas_names[:15])
        
        # Create network graph
        fig = create_network_graph(network_data)
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.info("This network graph shows how research areas are connected. A line between two areas indicates that they appear together in publications. Thicker lines represent stronger connections.")
    
    # Show correlation matrix for top areas
    st.subheader("🧩 Research Area Correlation Matrix")
    
    if len(cooccurrence) > 0:
        # Create correlation matrix
        corr_matrix = create_correlation_matrix(cooccurrence, top_areas_names[:10])
        
        fig = px.imshow(
            corr_matrix,
            labels=dict(x="Research Area", y="Research Area", color="Correlation"),
            x=corr_matrix.columns,
            y=corr_matrix.index,
            color_continuous_scale="RdBu_r",
            zmin=-1, zmax=1,
            height=600
        )
        
        fig.update_layout(
            margin=dict(l=10, r=10, t=10, b=10)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add explanation
        st.info("This correlation matrix shows how research areas tend to appear together. Positive values (blue) indicate areas that frequently co-occur, while negative values (red) indicate areas that rarely appear together.")

# Tab 4: Detailed Analysis
with tab4:
    st.markdown('<h2 class="sub-header">🔍 Detailed Research Area Analysis</h2>', unsafe_allow_html=True)
    
    # Allow user to select specific research area to analyze
    selected_area = st.selectbox(
        "Select a research area to analyze in detail",
        options=sorted(set([area for area, _ in get_top_areas(all_areas, n=50)]))
    )
    
    if selected_area:
        # Filter data for selected area
        area_data = filtered_df[filtered_df['research_areas'].str.contains(selected_area, na=False)]
        
        # Display key statistics
        st.subheader(f"📊 Statistics for {selected_area}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Publications", len(area_data))
        
        with col2:
            if len(area_data) > 0 and 'year' in area_data.columns:
                first_year = int(area_data['year'].min())
                st.metric("First Appearance", first_year)
        
        with col3:
            percentage = (len(area_data) / len(filtered_df)) * 100
            st.metric("Percentage of All Publications", f"{percentage:.1f}%")
        
        # Show trend over time for this area
        if 'year' in area_data.columns:
            st.subheader(f"📈 {selected_area} Publications Over Time")
            
            # Count publications by year
            area_by_year = area_data.groupby('year').size().reset_index(name='count')
            
            fig = px.bar(
                area_by_year,
                x='year',
                y='count',
                title=f"{selected_area} Publications by Year",
                color='count',
                color_continuous_scale='Viridis',
                height=400
            )
            
            fig.update_layout(
                xaxis_title="Year",
                yaxis_title="Number of Publications"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Show co-occurring research areas
        st.subheader(f"🤝 Research Areas that Co-occur with {selected_area}")
        
        cooccurring_areas = get_cooccurring_areas(filtered_df, selected_area, normalize=normalize_areas)
        
        if cooccurring_areas:
            cooccur_df = pd.DataFrame(cooccurring_areas, columns=['Research Area', 'Co-occurrences'])
            
            fig = px.bar(
                cooccur_df.head(15),
                y='Research Area',
                x='Co-occurrences',
                orientation='h',
                color='Co-occurrences',
                color_continuous_scale='Viridis',
                title=f"Top 15 Research Areas Co-occurring with {selected_area}",
                height=500
            )
            
            fig.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                xaxis_title="Number of Co-occurrences",
                yaxis_title="Research Area"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        # Show publications in this area
        st.subheader(f"📚 Publications in {selected_area}")
        
        if len(area_data) > 0:
            # Display simplified data table
            display_cols = ['research_areas', 'year'] if 'year' in area_data.columns else ['research_areas']
            st.dataframe(area_data[display_cols], height=300)
            
            # Allow download of filtered data
            csv = area_data.to_csv(index=False)
            st.download_button(
                label=f"Download {selected_area} Data as CSV",
                data=csv,
                file_name=f"{selected_area.replace(' ', '_').replace('&', 'and')}_research.csv",
                mime="text/csv"
            )