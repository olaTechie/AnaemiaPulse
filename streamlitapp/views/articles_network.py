import streamlit as st
from utils.vos_utils import setup_vos_styling, create_sidebar_info, display_vosviewer

# Page config
# st.set_page_config(
#     page_title="Research Similarity Network", 
#     page_icon="📄",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Apply common styling
setup_vos_styling()

# Page title and description
st.title("📄 Research Similarity Network")
st.markdown("See how research papers are connected through shared citations, revealing topic clusters and research fronts.")

# Create sidebar information
create_sidebar_info("Research Similarity")

# Display VOSviewer visualization
articles_url = "https://app.vosviewer.com/?json=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1WL46VTBRW01wqzbD5F1S8HTEOfVRQZ5d"
display_vosviewer(articles_url)