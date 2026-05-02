import streamlit as st
from utils.vos_utils import setup_vos_styling, create_sidebar_info, display_vosviewer

# # Page config
# st.set_page_config(
#     page_title="Country Citation Network",
#     page_icon="🌎",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Apply common styling
setup_vos_styling()

# Page title and description
st.title("🌎 Citation Network of Countries")
st.markdown("Visualize citation patterns between countries, highlighting international research influence and collaboration.")

# Create sidebar information
create_sidebar_info("Country Citation Network")

# Display VOSviewer visualization
countries_url = "https://app.vosviewer.com/?json=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1MasNQYam1sp_st7ggzTYg_KbEJyceflD"
display_vosviewer(countries_url)