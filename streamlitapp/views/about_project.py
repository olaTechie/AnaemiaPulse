import streamlit as st
from PIL import Image
import base64

# Set page configuration
# st.set_page_config(
#     page_title="Anaemia Research Dashboard",
#     page_icon="🔬",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #0D47A1;
        margin-bottom: 1rem;
    }
    .section-header {
        font-size: 1.8rem;
        font-weight: bold;
        color: #1976D2;
        margin-top: 1.5rem;
        margin-bottom: 0.8rem;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #2196F3;
    }
    .subsection-header {
        font-size: 1.4rem;
        font-weight: bold;
        color: #2196F3;
        margin-top: 1.2rem;
        margin-bottom: 0.5rem;
    }
    .feature-box {
        background-color: #f0f7ff;
        border-radius: 10px;
        padding: 1.2rem;
        margin-bottom: 1rem;
        border-left: 5px solid #2196F3;
    }
    .footnote {
        font-size: 0.9rem;
        font-style: italic;
        color: #455A64;
        margin-top: 2rem;
    }
    .emoji-heading {
        font-size: 1.8rem;
    }
    .feature-title {
        font-weight: bold;
        font-size: 1.1rem;
        color: #0D47A1;
    }
    .hover-box:hover {
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        transition: box-shadow 0.3s ease-in-out;
    }
</style>
""", unsafe_allow_html=True)

# Title section with logo
col1, col2 = st.columns([1, 5])

with col1:
    # PLACEHOLDER FOR LOGO
    # Add your logo image here
    st.image("attached_assets/logo.png", width=120)
    # st.image("/api/placeholder/120/120", width=120)  # Placeholder
    
with col2:
    st.markdown('<div class="main-header">Mapping the Landscape of Anaemia Research in Women 🔬🔍</div>', unsafe_allow_html=True)
    st.markdown("### A Bibliometric Analysis and Topic Modelling of the Literature")

# Hero image section
# PLACEHOLDER FOR HERO IMAGE
# st.image("attached_assets/hero_image.png", use_container_width=True)
# st.image("/api/placeholder/1200/300", use_column_width=True)  # Placeholder

# Project Overview section
st.markdown('<div class="section-header">📋 Project Overview</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 2])

with col1:
    st.markdown("""
    This interactive dashboard presents findings from a comprehensive bibliometric analysis and topic modeling study of anaemia research in women. By analyzing publication patterns, research themes, and collaboration networks, we aim to identify trends, knowledge gaps, and future research priorities in this critical health area.
    
    Our analysis provides valuable insights for researchers, healthcare professionals, policymakers, and funding agencies interested in advancing anaemia research and improving women's health outcomes globally.
    """)

with col2:
    # PLACEHOLDER FOR OVERVIEW IMAGE
    st.image("attached_assets/overview_diagram.png", width=300)
    # st.image("/api/placeholder/400/300", use_column_width=True)  # Placeholder

# Research Methodology section
st.markdown('<div class="section-header">🔬 Research Methodology</div>', unsafe_allow_html=True)

methodology_tabs = st.tabs(["Bibliometric Analysis 📊", "Topic Modelling 🧠", "Impact Analysis 🌟"])

with methodology_tabs[0]:
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # PLACEHOLDER FOR BIBLIOMETRIC IMAGE
        st.image("attached_assets/bibliometric_analysis.png", width=300)
        # st.image("/api/placeholder/300/300", use_column_width=True)  # Placeholder
        
    with col2:
        st.markdown("### Bibliometric Analysis Approach")
        st.markdown("""
        We systematically analyzed publication data from PubMed and Web of Science databases to map the knowledge structure and evolution of anaemia research:
        
        - 📈 Publication trends and citation patterns
        - 👥 Leading researchers, institutions, and countries
        - 🔗 Co-authorship and collaboration networks
        - 📰 Journal co-citation networks
        - 📑 Document clustering and citation relationships
        
        Data was collected through a structured search using MeSH terms and keywords related to anaemia and women's health, with standardized cleaning and processing procedures.
        """)

with methodology_tabs[1]:
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("### Topic Modelling Approach")
        st.markdown("""
        Using latent Dirichlet allocation (LDA), we identified key thematic areas and tracked their evolution over time:
        
        - 🗂️ Major research themes and their interrelationships
        - 📈 Emerging and declining topic areas
        - ⏳ Temporal trends in research focus
        - 🧩 Knowledge gaps requiring further investigation
        
        Text data from titles and abstracts underwent pre-processing to remove stop words, perform lemmatization, and identify key phrases. Model hyperparameters were optimized to maximize topic coherence and clarity.
        """)
        
    with col2:
        # PLACEHOLDER FOR TOPIC MODEL IMAGE
        st.image("attached_assets/topic_model.png", use_container_width=True)
        # st.image("/api/placeholder/300/300", use_column_width=True)  # Placeholder

with methodology_tabs[2]:
    col1, col2 = st.columns([2, 3])
    
    with col1:
        # PLACEHOLDER FOR BIBLIOMETRIC IMAGE
        st.image("attached_assets/impact_analysis.png", width=300)
        # st.image("/api/placeholder/300/300", use_column_width=True)  # Placeholder
        
    with col2:
        st.markdown("### Impact Analysis Approach")
        st.markdown("""
        Our Impact Analysis provides a multidimensional assessment of research influence and reach in maternal anaemia studies. 
        This section offers:
        
        - **Citation Analysis**: Discover the most influential papers and citation patterns shaping the field
        
        - **Journal Impact**: Explore key publication venues and their relative importance in disseminating research
        
        - **Geographic Impact**: Visualize how research output and citation patterns vary across regions
        
        - **Emerging Influence**: Track rising stars and breakthrough studies gaining rapid recognition
        
        - **Interdisciplinary Reach**: Examine how anaemia research connects with and influences other medical disciplines
        
        These impact metrics help identify research that drives innovation and guides clinical practice, highlighting work with the greatest potential to improve maternal health outcomes worldwide.
        """)
      

# Dashboard Features section
st.markdown('<div class="section-header">💻 Dashboard Features</div>', unsafe_allow_html=True)
st.markdown("This interactive data exploration platform allows users to engage with the research landscape through multiple interconnected views:")

# Create three columns for the first row of features
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="feature-box hover-box">', unsafe_allow_html=True)
    st.markdown('<p class="emoji-heading">📊</p>', unsafe_allow_html=True)
    st.markdown('<p class="feature-title">Research Insights</p>', unsafe_allow_html=True)
    st.markdown("""
    - **Overview**: At-a-glance summary dashboard
    - **Research Areas**: Topic distribution analysis
    - **Funding Analysis**: Funding patterns exploration
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="feature-box hover-box">', unsafe_allow_html=True)
    st.markdown('<p class="emoji-heading">🔗</p>', unsafe_allow_html=True)
    st.markdown('<p class="feature-title">Network Analysis</p>', unsafe_allow_html=True)
    st.markdown("""
    - **Journal Citation Network**: Citation patterns
    - **Research Similarity Network**: Study relationships
    - **Country Citation Network**: Global contributions
    - **Collaboration Networks**: Partnership mapping
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="feature-box hover-box">', unsafe_allow_html=True)
    st.markdown('<p class="emoji-heading">🔍</p>', unsafe_allow_html=True)
    st.markdown('<p class="feature-title">Analysis Tools</p>', unsafe_allow_html=True)
    st.markdown("""
    - **Authors Discovery**: Influential researcher identification
    - **Topics Discovery**: Advanced thematic analysis
    - **Knowledge Base**: Comprehensive reference repository
    """)
    st.markdown('</div>', unsafe_allow_html=True)



# How to Use section
st.markdown('<div class="section-header">🔎 How to Use This Dashboard</div>', unsafe_allow_html=True)

how_to_use_expander = st.expander("Click to expand usage instructions", expanded=True)
with how_to_use_expander:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("""
        ### Navigation
        - Use the navigation panel on the left to explore different aspects of the analysis
        - Each page offers interactive visualizations with filtering capabilities
        - Hover over chart elements to see detailed information
        
        ### Filtering Data
        - Use dropdown menus, sliders, and search boxes to refine your view
        - Apply multiple filters to drill down into specific subsets of data
        - Reset filters using the "Reset" button when available
        """)
        
    with col2:
        st.markdown("""
        ### Visualization Tools
        - Click and drag to zoom into specific areas of charts
        - Use legends to toggle visibility of data series
        - Download visualization data or images using the export options
        
        ### Getting Help
        - Look for information icons (ℹ️) for additional context
        - Refer to the Knowledge Base section for methodology details
        - Contact the research team with specific questions
        """)

# Funding & Acknowledgments section
st.markdown('<div class="section-header">🏆 Funding & Acknowledgments</div>', unsafe_allow_html=True)
st.markdown("""
This project was funded by the World Health Organization (WHO) as part of global efforts to address anaemia in women. We gratefully acknowledge the contributions of our research team and collaborating institutions.

**Project Team:**
- Olalekan A. Uthman, Warwick Centre for Global Health Research, Applied Health, Warwick Medical School, The University of Warwick, Coventry, UK.
- Tabassum Firoz, Yale New Haven Health, New Haven, Connecticut, USA.
- María Barreix, UNDP/UNFPA/UNICEF/WHO/World Bank Special Programme of Research, Development and Research Training in Human Reproduction (HRP),Department of Sexual and Reproductive Health and Research, World Health Organization, Geneve, Switzerland.
- Lisa M Rogers, Department of Nutrition and Food Safety, World Health Organization (WHO), Geneva, Switzerland.


""")

# Call to action
st.markdown("")
col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    st.markdown('<div class="feature-box" style="text-align: center; background-color: #e3f2fd;">', unsafe_allow_html=True)
    st.markdown("### Begin Exploring the Dashboard")
    st.markdown("Use the navigation menu on the left to start exploring the different sections of the dashboard.")
    st.markdown('</div>', unsafe_allow_html=True)

# Footer with citation information
st.markdown('<div class="footnote">', unsafe_allow_html=True)
st.markdown("""
**Suggested Citation:** Uthman OA, Firoz T, Barreix M, Rogers LM. (2025). Mapping the Landscape of Anaemia Research in Women: A Bibliometric Analysis and Topic Modelling of the Literature (https://maternalanemia.streamlit.app/).

Last Updated: April 2025
""")
st.markdown('</div>', unsafe_allow_html=True)