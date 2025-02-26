import streamlit as st
from utils.vos_utils import setup_vos_styling, create_sidebar_info, display_vosviewer

# Page config
# st.set_page_config(
#     page_title="Author Co-authorship Network",
#     page_icon="👥",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Apply common styling
setup_vos_styling()

# Page title and description
st.title("👥 Co-authorship Network of Authors")
st.markdown("Discover collaboration patterns between researchers and identify key research communities.")

# Create sidebar information
create_sidebar_info("Author Co-authorship Network")

# Display VOSviewer visualization
authors_url = "https://app.vosviewer.com/?json=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1kK8O-v0pPgcPkICf3yaaMUwIcTA6xx8r"
display_vosviewer(authors_url)