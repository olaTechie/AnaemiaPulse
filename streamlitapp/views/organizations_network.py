import streamlit as st
from utils.vos_utils import setup_vos_styling, create_sidebar_info, display_vosviewer

# # Page config
# st.set_page_config(
#     page_title="Organization Co-authorship Network",
#     page_icon="🏢",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Apply common styling
setup_vos_styling()

# Page title and description
st.title("🏢 Co-authorship Network of Organizations")
st.markdown("Explore collaboration patterns between universities, research institutes, and other organizations.")

# Create sidebar information
create_sidebar_info("Organization Co-authorship Network")

# Display VOSviewer visualization
organizations_url = "https://app.vosviewer.com/?json=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1z19bV8fma_B2O2Zmq7Wn8c0zqW59NT6D"
display_vosviewer(organizations_url)