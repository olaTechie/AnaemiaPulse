import streamlit as st
from utils.vos_utils import setup_vos_styling, create_sidebar_info, display_vosviewer

# Page config
# st.set_page_config(
#     page_title="Journal Citation Network",
#     page_icon="📚",
#     layout="wide",
#     initial_sidebar_state="expanded"
# )

# Apply common styling
setup_vos_styling()

# Page title and description
st.title("📚 Citation Network of Journals")
st.markdown("Explore how academic journals cite each other, revealing influential sources and journal communities.")

# Create sidebar information
create_sidebar_info("Journal Citation Network")

# Display VOSviewer visualization
journals_url = "https://app.vosviewer.com/?json=https%3A%2F%2Fdrive.google.com%2Fuc%3Fid%3D1dWtANsyLZ9fLF3gpcokD2KIznbVJNqHt"
display_vosviewer(journals_url)