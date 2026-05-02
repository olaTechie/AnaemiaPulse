import pandas as pd
import numpy as np
import re

class DataProcessor:
    def __init__(self, data_path):
        self.df = pd.read_excel(data_path)
        self.preprocess_data()
        
    def extract_country(self, address):
        """
        Extract country name from address string.
        
        Args:
            address (str): Full address string
            
        Returns:
            str: Extracted country name or 'Unknown' if not found
        """
        if pd.isna(address):
            return 'Unknown'
            
        # Common country mappings including special cases
        country_mappings = {
            'USA': 'United States',
            'US': 'United States',
            'UK': 'United Kingdom',
            'ENGLAND': 'United Kingdom',
            'BRITAIN': 'United Kingdom',
            'UAE': 'United Arab Emirates'
        }
        
        # Remove any trailing/leading whitespace and convert to uppercase
        address = str(address).strip().upper()
        
        # Handle USA special case (when it appears with state)
        usa_pattern = r'.*[,\s]([A-Z]{2})\s+USA$'
        usa_match = re.search(usa_pattern, address)
        if usa_match or address.endswith('USA'):
            return 'United States'
        
        # Extract the last component of the address
        components = [x.strip() for x in address.split(',')]
        potential_country = components[-1].strip()
        
        # Check if it's in our mappings
        if potential_country in country_mappings:
            return country_mappings[potential_country]
        
        return potential_country if potential_country else 'Unknown'

    def preprocess_data(self):
        """Clean and preprocess the data."""
        # Clean and standardize year field
        self.df['year'] = pd.to_numeric(self.df['year'], errors='coerce')
        
        # Create author list from author string
        self.df['author_list'] = self.df['author'].str.split(' and ')
        
        # Process affiliations
        self.df['affiliation_list'] = self.df['affiliation'].str.split(';')
        
        # Extract countries using the enhanced method
        self.df['countries'] = self.df['address'].apply(self.extract_country)
        
        # Clean citation counts
        self.df['citations'] = self.df['usage_count_since_2013'].fillna(0)

    def get_kpi_metrics(self, df=None):
        """Get KPI metrics from the data, optionally using a filtered dataframe."""
        df = df if df is not None else self.df
        return {
            'total_articles': len(df),
            'total_authors': df['author_list'].explode().nunique(),
            'total_institutions': df['affiliation_list'].explode().nunique(),
            'total_countries': df['countries'].nunique(),
            'total_citations': df['citations'].sum()
        }

    def get_yearly_trends(self, df=None):
        """Get yearly publication and citation trends, optionally using a filtered dataframe."""
        df = df if df is not None else self.df
        yearly_pubs = df.groupby('year').size().reset_index(name='publications')
        yearly_citations = df.groupby('year')['citations'].sum().reset_index()
        return yearly_pubs, yearly_citations

    def get_top_contributors(self, n=10, df=None):
        """Get top contributors, optionally using a filtered dataframe."""
        df = df if df is not None else self.df
        top_authors = df['author_list'].explode().value_counts().head(n)
        top_countries = df['countries'].value_counts().head(n)
        top_institutions = df['affiliation_list'].explode().value_counts().head(n)
        return top_authors, top_countries, top_institutions

    def get_country_statistics(self, df=None):
        """Get detailed country statistics."""
        df = df if df is not None else self.df
        country_stats = pd.DataFrame({
            'publication_count': df['countries'].value_counts(),
            'citation_count': df.groupby('countries')['citations'].sum(),
            'unique_authors': df.groupby('countries')['author_list'].apply(
                lambda x: len(set([author for sublist in x for author in sublist]))
            ),
            'unique_institutions': df.groupby('countries')['affiliation_list'].apply(
                lambda x: len(set([inst.strip() for sublist in x for inst in sublist]))
            )
        }).fillna(0)
        
        # Calculate average citations per publication
        country_stats['avg_citations_per_pub'] = (
            country_stats['citation_count'] / country_stats['publication_count']
        ).round(2)
        
        return country_stats.sort_values('publication_count', ascending=False)