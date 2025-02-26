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
        
        # Create a standardized country name for aggregation
        df_map['country_upper'] = df_map['country'].str.upper().str.strip()
        
        # Aggregate duplicate countries (sum their counts)
        df_agg = df_map.groupby('country_upper').agg({'count': 'sum'}).reset_index()
        
        # Keep track of original country names for display purposes
        country_case_map = {}
        for _, row in df_map.iterrows():
            # Prefer longer names and names with higher counts
            if row['country_upper'] not in country_case_map or \
            (len(row['country']) > len(country_case_map[row['country_upper']]) and row['count'] >= 
                df_map[df_map['country'] == country_case_map[row['country_upper']]]['count'].values[0]):
                country_case_map[row['country_upper']] = row['country']
        
        # Map the uppercase country names back to proper case
        df_agg['country'] = df_agg['country_upper'].map(lambda x: country_case_map.get(x, x))
        
        # Drop the temporary uppercase column
        df_map = df_agg[['country', 'count']]
        
        # Print debug info
        # print(f"After aggregation: {len(df_map)} unique countries")
        
        # Convert country names to ISO codes where possible (for better mapping)
        country_name_to_code = {
            # Common country name variations
            'USA': 'USA', 'UNITED STATES': 'USA', 'United States': 'USA', 'U.S.A.': 'USA', 
            'US': 'USA', 'UNITED STATES OF AMERICA': 'USA', 'United States of America': 'USA',
            
            'UK': 'GBR', 'UNITED KINGDOM': 'GBR', 'United Kingdom': 'GBR', 'GREAT BRITAIN': 'GBR', 
            'Great Britain': 'GBR', 'ENGLAND': 'GBR', 'England': 'GBR',
            
            'CHINA': 'CHN', 'PEOPLES R CHINA': 'CHN', "People's Republic of China": 'CHN',
            'PRC': 'CHN', 'Mainland China': 'CHN',
            
            'INDIA': 'IND', 'Republic of India': 'IND',
            
            'CANADA': 'CAN', 'AUSTRALIA': 'AUS', 'BRAZIL': 'BRA',
            'GERMANY': 'DEU', 'Germany': 'DEU', 'Deutschland': 'DEU',
            'FRANCE': 'FRA', 'ITALY': 'ITA', 'SPAIN': 'ESP',
            
            'RUSSIA': 'RUS', 'RUSSIAN FEDERATION': 'RUS', 'Russia': 'RUS',
            
            'JAPAN': 'JPN', 'SOUTH KOREA': 'KOR', 'KOREA': 'KOR', 'Republic of Korea': 'KOR',
            
            'SOUTH AFRICA': 'ZAF', 'NIGERIA': 'NGA', 'KENYA': 'KEN', 'ETHIOPIA': 'ETH',
            'UGANDA': 'UGA', 'GHANA': 'GHA', 'CAMEROON': 'CMR', 'SENEGAL': 'SEN',
            
            'SWEDEN': 'SWE', 'NORWAY': 'NOR', 'FINLAND': 'FIN', 'DENMARK': 'DNK',
            
            'NETHERLANDS': 'NLD', 'THE NETHERLANDS': 'NLD', 'HOLLAND': 'NLD', 'Netherlands': 'NLD',
            
            'BELGIUM': 'BEL', 'SWITZERLAND': 'CHE', 'AUSTRIA': 'AUT', 
            'POLAND': 'POL', 'TURKEY': 'TUR', 'TURKIYE': 'TUR', 'GREECE': 'GRC',
            
            'MEXICO': 'MEX', 'ARGENTINA': 'ARG', 'CHILE': 'CHL', 'COLOMBIA': 'COL', 
            'PERU': 'PER', 'VENEZUELA': 'VEN', 'ECUADOR': 'ECU',
            
            'THAILAND': 'THA', 'INDONESIA': 'IDN', 'MALAYSIA': 'MYS', 'SINGAPORE': 'SGP',
            'VIETNAM': 'VNM', 'PHILIPPINES': 'PHL', 'MYANMAR': 'MMR', 'BURMA': 'MMR',
            
            'PAKISTAN': 'PAK', 'BANGLADESH': 'BGD', 'SRI LANKA': 'LKA', 'NEPAL': 'NPL',
            
            'IRAN': 'IRN', 'IRAQ': 'IRQ', 'SAUDI ARABIA': 'SAU', 'KUWAIT': 'KWT',
            'UNITED ARAB EMIRATES': 'ARE', 'UAE': 'ARE', 'U ARAB EMIRATES': 'ARE', 'QATAR': 'QAT', 'OMAN': 'OMN',
            
            'ISRAEL': 'ISR', 'EGYPT': 'EGY', 'MOROCCO': 'MAR', 'TUNISIA': 'TUN',
            'ALGERIA': 'DZA', 'LIBYA': 'LBY', 'SUDAN': 'SDN', 'TANZANIA': 'TZA',
            
            'NEW ZEALAND': 'NZL', 'PAPUA NEW GUINEA': 'PNG', 'FIJI': 'FJI',
            
            'IRELAND': 'IRL', 'PORTUGAL': 'PRT', 'ROMANIA': 'ROU', 'HUNGARY': 'HUN',
            'CZECH REPUBLIC': 'CZE', 'CZECHIA': 'CZE', 'SLOVAKIA': 'SVK', 'SLOVENIA': 'SVN',
            'CROATIA': 'HRV', 'SERBIA': 'SRB', 'BULGARIA': 'BGR', 'UKRAINE': 'UKR',
            'BELARUS': 'BLR', 'LITHUANIA': 'LTU', 'LATVIA': 'LVA', 'ESTONIA': 'EST',
            
            # Special cases from your data
            'TAIWAN': 'TWN', 'Taiwan': 'TWN',
            'HONG KONG': 'HKG', 'Hong Kong': 'HKG',
            'CUBA': 'CUB',
            'ARMENIA': 'ARM',
        }
        
        # Add custom mapping function with fallbacks
        def map_country_to_code(country_name):
            # Direct mapping
            if country_name in country_name_to_code:
                return country_name_to_code[country_name]
            
            # Try uppercased version
            upper_name = country_name.upper()
            if upper_name in country_name_to_code:
                return country_name_to_code[upper_name]
            
            # Try with common cleanup
            cleaned_name = upper_name.replace("  ", " ").strip()
            if cleaned_name in country_name_to_code:
                return country_name_to_code[cleaned_name]
                
            # Default fallback: return the original name (px.choropleth will try to match it)
            return country_name
        
        # Apply country code conversion
        df_map['iso_alpha'] = df_map['country'].apply(map_country_to_code)
        
        # Debug: print countries and their ISO codes
        # print("Countries in dataset:")
        # for idx, row in df_map.iterrows():
        #     print(f"Country: {row['country']}, Count: {row['count']}, ISO: {row['iso_alpha']}")
        
        if discrete_colors:
            # Create discrete color bins
            bins = [0, 10, 50, 100, 250, 500, 1000, float('inf')]
            labels = ['1-10', '11-50', '51-100', '101-250', '251-500', '501-1000', '1000+']
            
            # Add a categorical column for the bins
            df_map['count_category'] = pd.cut(df_map['count'], bins=bins, labels=labels, right=False)
            
            # # Debug: print country categories
            # print("Country categories:")
            # for idx, row in df_map.iterrows():
            #     print(f"Country: {row['country']}, Count: {row['count']}, Category: {row['count_category']}")
            
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