import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import networkx as nx
import numpy as np
import pandas as pd

class Visualizer:
    def __init__(self, color_scheme=px.colors.qualitative.Set3):
        self.colors = color_scheme

    def create_yearly_trends_plot(self, yearly_pubs, yearly_citations):
        fig = make_subplots(specs=[[{"secondary_y": True}]])

        fig.add_trace(
            go.Scatter(x=yearly_pubs['year'], y=yearly_pubs['publications'],
                      name="Publications", line=dict(color=self.colors[0])),
            secondary_y=False
        )

        fig.add_trace(
            go.Scatter(x=yearly_citations['year'], y=yearly_citations['citations'],
                      name="Citations", line=dict(color=self.colors[1])),
            secondary_y=True
        )

        fig.update_layout(
            title="Publication and Citation Trends",
            xaxis_title="Year",
            yaxis_title="Number of Publications",
            yaxis2_title="Number of Citations",
            # Mobile-friendly layout
            margin=dict(l=10, r=10, t=40, b=20),
            height=300,  # Reduced height for mobile
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            # Improved touch interaction
            dragmode='pan',
            showlegend=True
        )

        return fig

    def create_top_contributors_plot(self, data, title):
        fig = go.Figure(data=[
            go.Bar(x=data.values, y=data.index, orientation='h',
                  marker_color=self.colors[2])
        ])

        fig.update_layout(
            title=title,
            xaxis_title="Count",
            yaxis_title="",
            # Mobile-friendly layout
            height=min(300 + len(data) * 20, 500),  # Dynamic height based on data
            margin=dict(l=10, r=10, t=40, b=20),
            yaxis=dict(
                tickfont=dict(size=10),  # Smaller font for mobile
                automargin=True  # Ensure labels are visible
            ),
            dragmode='pan',
            showlegend=False
        )

        return fig


    # def create_world_map(self, country_counts, discrete_colors=True):

    def create_world_map(self, country_counts, discrete_colors=True):
        """
        Create an improved world map visualization with discrete color categories
        
        Args:
            country_counts (pd.Series): Series with country names as index and counts as values
            discrete_colors (bool, optional): Whether to use discrete color categories. Defaults to True.
        
        Returns:
            plotly.graph_objects.Figure: World map figure
        """
        import plotly.express as px
        import plotly.graph_objects as go
        import pandas as pd
        import numpy as np
        
        # Create a DataFrame for the map
        df_map = pd.DataFrame({
            'country': country_counts.index,
            'count': country_counts.values
        })
        
        # Convert country names to ISO codes where possible (for better mapping)
        country_name_to_code = {
            'USA': 'USA', 'United States': 'USA', 'U.S.A.': 'USA', 'United States of America': 'USA', 'US': 'USA',
            'UK': 'GBR', 'United Kingdom': 'GBR', 'Great Britain': 'GBR', 'England': 'GBR',
            'China': 'CHN', "People's Republic of China": 'CHN',
            'India': 'IND', 'Republic of India': 'IND',
            'Canada': 'CAN', 'Australia': 'AUS', 'Brazil': 'BRA',
            'Germany': 'DEU', 'France': 'FRA', 'Italy': 'ITA', 'Spain': 'ESP',
            'Russia': 'RUS', 'Russian Federation': 'RUS',
            'Japan': 'JPN', 'South Korea': 'KOR', 'Korea': 'KOR', 'Republic of Korea': 'KOR',
            'South Africa': 'ZAF', 'Nigeria': 'NGA', 'Kenya': 'KEN', 'Ethiopia': 'ETH',
            'Sweden': 'SWE', 'Norway': 'NOR', 'Finland': 'FIN', 'Denmark': 'DNK',
            'Netherlands': 'NLD', 'The Netherlands': 'NLD', 'Holland': 'NLD',
            'Belgium': 'BEL', 'Switzerland': 'CHE', 'Austria': 'AUT', 
            'Poland': 'POL', 'Turkey': 'TUR', 'Greece': 'GRC',
            'Mexico': 'MEX', 'Argentina': 'ARG', 'Chile': 'CHL', 'Colombia': 'COL', 
            'Peru': 'PER', 'Venezuela': 'VEN', 'Ecuador': 'ECU',
            'Thailand': 'THA', 'Indonesia': 'IDN', 'Malaysia': 'MYS', 'Singapore': 'SGP',
            'Vietnam': 'VNM', 'Philippines': 'PHL', 'Myanmar': 'MMR', 'Burma': 'MMR',
            'Pakistan': 'PAK', 'Bangladesh': 'BGD', 'Sri Lanka': 'LKA', 'Nepal': 'NPL',
            'Iran': 'IRN', 'Iraq': 'IRQ', 'Saudi Arabia': 'SAU', 'Kuwait': 'KWT',
            'United Arab Emirates': 'ARE', 'UAE': 'ARE', 'Qatar': 'QAT', 'Oman': 'OMN',
            'Israel': 'ISR', 'Egypt': 'EGY', 'Morocco': 'MAR', 'Tunisia': 'TUN',
            'Algeria': 'DZA', 'Libya': 'LBY', 'Sudan': 'SDN', 'Tanzania': 'TZA',
            'Uganda': 'UGA', 'Ghana': 'GHA', 'Cameroon': 'CMR', 'Senegal': 'SEN',
            'New Zealand': 'NZL', 'Papua New Guinea': 'PNG', 'Fiji': 'FJI',
            'Ireland': 'IRL', 'Portugal': 'PRT', 'Romania': 'ROU', 'Hungary': 'HUN',
            'Czech Republic': 'CZE', 'Czechia': 'CZE', 'Slovakia': 'SVK', 'Slovenia': 'SVN',
            'Croatia': 'HRV', 'Serbia': 'SRB', 'Bulgaria': 'BGR', 'Ukraine': 'UKR',
            'Belarus': 'BLR', 'Lithuania': 'LTU', 'Latvia': 'LVA', 'Estonia': 'EST',
        }
        
        # Add custom regex-based matching for special cases
        def map_country_to_code(country_name):
            if country_name in country_name_to_code:
                return country_name_to_code[country_name]
            
            # Try lowercase comparison
            lower_name = country_name.lower()
            for name, code in country_name_to_code.items():
                if name.lower() == lower_name:
                    return code
            
            # Default: return the original name (px.choropleth will try to match it)
            return country_name
        
        # Apply country code conversion
        df_map['iso_alpha'] = df_map['country'].apply(map_country_to_code)
        
        if discrete_colors:
            # Create discrete color bins
            bins = [0, 10, 50, 100, 250, 500, 1000, float('inf')]
            labels = ['1-10', '11-50', '51-100', '101-250', '251-500', '501-1000', '1000+']
            
            # Add a categorical column for the bins
            df_map['count_category'] = pd.cut(df_map['count'], bins=bins, labels=labels, right=False)
            
            # Define custom colors with bright colors for small values
            # Use a distinctive palette that makes smaller values more visible
            custom_colors = ['#FF69B4', '#FFD700', '#1E90FF', '#32CD32', '#00CED1', '#9370DB', '#8B008B']
            
            # Create the choropleth map with discrete colors
            fig = px.choropleth(
                df_map,
                locations="iso_alpha",
                color="count_category",
                hover_name="country",
                hover_data={"count": True, "iso_alpha": False, "count_category": False},
                projection="natural earth",
                color_discrete_map=dict(zip(labels, custom_colors)),
                title="Global Distribution of Research",
                labels={'count_category': 'Number of Publications', 'count': 'Publications'}
            )
        else:
            # Original continuous color scale approach
            fig = px.choropleth(
                df_map,
                locations="iso_alpha",
                color="count",
                hover_name="country",
                projection="natural earth",
                color_continuous_scale="Viridis",
                title="Global Distribution of Research",
                labels={'count': 'Number of Publications'}
            )
        
        # Improve overall map appearance
        fig.update_layout(
            margin=dict(l=0, r=0, t=50, b=0),
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="lightgray",
                showland=True,
                landcolor="whitesmoke",
                showocean=True,
                oceancolor="aliceblue",
                showcountries=True,
                countrycolor="gray",
                projection_type="natural earth"
            )
        )
        
        # Add annotations for top countries
        top_countries = df_map.nlargest(3, 'count')
        annotations = []
        
        for i, (_, row) in enumerate(top_countries.iterrows()):
            annotations.append(
                dict(
                    x=0.5,  # Center position 
                    y=0.1 + (i * 0.05),  # Position from bottom
                    xref="paper",
                    yref="paper",
                    text=f"{row['country']}: {row['count']} publications",
                    showarrow=False,
                    font=dict(size=12, color="black"),
                    align="center",
                    bgcolor="rgba(255, 255, 255, 0.7)",
                    bordercolor="gray",
                    borderwidth=1,
                    borderpad=4
                )
            )
        
        fig.update_layout(annotations=annotations)
        
        # Increase the opacity for all countries to ensure visibility
        fig.update_traces(marker_line_width=0.5, marker_opacity=0.8)
        
        return fig



    def create_network_graph(self, G):
        if len(G.nodes()) == 0:
            return go.Figure()

        # Optimize layout for mobile
        pos = nx.spring_layout(G, 
                            k=1/np.sqrt(len(G.nodes())), 
                            iterations=20)

        edge_x, edge_y = [], []
        edge_weights = nx.get_edge_attributes(G, 'weight')
        max_weight = max(edge_weights.values()) if edge_weights else 1

        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines',
            opacity=0.5
        )

        # Process nodes with optimized layout
        communities = nx.get_node_attributes(G, 'community')
        node_traces = []

        for comm_id in set(communities.values()):
            comm_nodes = [n for n, c in communities.items() if c == comm_id]

            node_x = []
            node_y = []
            node_text = []
            node_size = []

            for node in comm_nodes:
                x, y = pos[node]
                node_x.append(x)
                node_y.append(y)

                citations = G.nodes[node].get('citations', 0)
                publications = G.nodes[node].get('publications', 0)
                centrality = G.nodes[node].get('centrality', 0)

                node_text.append(
                    f"Author: {node}<br>"
                    f"Publications: {publications}<br>"
                    f"Citations: {citations}<br>"
                    f"Centrality: {centrality:.2f}"
                )
                node_size.append(centrality * 50)  # Reduced size for mobile

            node_trace = go.Scatter(
                x=node_x, y=node_y,
                mode='markers',
                hoverinfo='text',
                text=node_text,
                marker=dict(
                    size=node_size,
                    sizemode='area',
                    sizeref=2.*max(node_size)/(30.**2),  # Adjusted for mobile
                    sizemin=4,
                    color=self.colors[comm_id % len(self.colors)],
                    line=dict(width=1)
                ),
                name=f'Community {comm_id}'
            )
            node_traces.append(node_trace)

        fig = go.Figure(data=[edge_trace] + node_traces)
        fig.update_layout(
            title="Author Collaboration Network",
            showlegend=True,
            hovermode='closest',
            # Mobile-friendly layout
            margin=dict(l=5, r=5, t=40, b=20),
            height=400,  # Reduced height for mobile
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1
            ),
            dragmode='pan',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
        fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)

        return fig

    def create_keyword_network(self, G):
        """Create an interactive visualization of the keyword network."""
        if len(G.nodes()) == 0:
            return go.Figure()

        # Create layout
        pos = nx.spring_layout(G, k=1/np.sqrt(len(G.nodes())), iterations=50)

        # Create edges
        edge_x, edge_y = [], []
        edge_weights = []
        for edge in G.edges(data=True):
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
            edge_weights.extend([edge[2].get('weight', 1), edge[2].get('weight', 1), None])

        edge_trace = go.Scatter(
            x=edge_x, y=edge_y,
            line=dict(width=1, color='#888'),
            hoverinfo='none',
            mode='lines',
            opacity=0.5
        )

        # Create nodes
        node_x, node_y = [], []
        node_text = []
        node_size = []

        for node in G.nodes():
            x, y = pos[node]
            node_x.append(x)
            node_y.append(y)
            centrality = G.nodes[node].get('centrality', 0)
            degree = G.degree(node)
            node_text.append(f"Keyword: {node}<br>Connections: {degree}")
            node_size.append(centrality * 50)  # Scale for mobile

        node_trace = go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text',
            hoverinfo='text',
            text=node_text,
            textposition="top center",
            textfont=dict(size=8),  # Smaller text for mobile
            marker=dict(
                size=node_size,
                sizemode='area',
                sizeref=2.*max(node_size)/(30.**2),  # Adjusted for mobile
                sizemin=4,
                color=self.colors[0],
                line=dict(width=1)
            )
        )

        # Create figure with mobile-friendly layout
        fig = go.Figure(data=[edge_trace, node_trace])
        fig.update_layout(
            title="Keyword Co-occurrence Network",
            showlegend=False,
            hovermode='closest',
            margin=dict(l=5, r=5, t=40, b=20),
            height=400,  # Reduced height for mobile
            dragmode='pan',
            plot_bgcolor='white',
            paper_bgcolor='white'
        )

        fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False)
        fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False)

        return fig