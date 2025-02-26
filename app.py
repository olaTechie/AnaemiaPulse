import streamlit as st

st.set_page_config(
    page_icon="📊",
    # page_icon="🩸📊",
    layout="wide",
    initial_sidebar_state="expanded")


# --- PAGE SETUP ---
home_page = st.Page(
    "views/home.py",
    title="Overview",
    icon=":material/home:",
    default=True,
)

research_areas_page = st.Page(
    "views/research_areas_analysis.py",
    title="Research Areas",
    icon=":material/search_insights:",
)

funding_page = st.Page(
    "views/funding_analysis.py",
    title="Funding Analysis",
    icon=":material/money:",
)

journals_page = st.Page(
    "views/journals_network.py",
    title="Journal Citation Network",
    icon=":material/menu_book:",
)

articles_page = st.Page(
    "views/articles_network.py",
    title="Research Similarity Network",
    icon=":material/article:",
)

countries_page = st.Page(
    "views/countries_network.py",
    title="Country Citation Network",
    icon=":material/public:",
)

authors_page = st.Page(
    "views/authors_network.py",
    title="Author Co-authorship Network",
    icon=":material/people:",
)

organizations_page = st.Page(
    "views/organizations_network.py",
    title="Organization Co-authorship Network",
    icon=":material/business:",
)


visualization_page = st.Page(
    "views/author_discovery.py",
    title="Authors Discovery",
    icon=":material/analytics:",
)

data_explorer_page = st.Page(
    "views/topic_discovery.py",
    title="Topics Discovery",
    icon=":material/database:",
)

references_page = st.Page(
    "views/references.py",
    title="References",
    icon=":material/description:",
)

# askme_page = st.Page(
#     "views/ask_me.py",
#     title="Ask Me Anything",
#     icon=":material/description:",
# )
# # summary_page = st.Page(
#     "views/summary.py",
#     title="Summary Report",
#     icon=":material/folder:",
# )

# --- NAVIGATION SETUP WITH SECTIONS ---
pg = st.navigation(
    {
        "Research Insights": [home_page, research_areas_page, funding_page],
        "Citation Networks": [journals_page, articles_page, countries_page],
        "Collaboration Networks": [authors_page, organizations_page],
        "Analysis Tools": [visualization_page, data_explorer_page],
        "Knowledge Base": [references_page],
    }
)

# --- SHARED ON ALL PAGES ---


# --- RUN NAVIGATION ---
pg.run()