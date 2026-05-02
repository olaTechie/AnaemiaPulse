import streamlit as st
import streamlit.components.v1 as components

def setup_vos_styling():
    """Add common CSS styling for VOSviewer pages"""
    st.markdown("""
        <style>
            .stApp {
                margin: 0;
                padding: 0;
            }
            .vosviewer-container {
                width: 100%;
                min-height: 800px;
                border: 1px solid #ddd;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .material-icon {
                margin-right: 8px;
                vertical-align: middle;
            }
            /* Hide Streamlit footer */
            footer {
                visibility: hidden;
            }
            /* Adjust sidebar width */
            [data-testid="stSidebar"][aria-expanded="true"] {
                min-width: 300px;
                max-width: 350px;
            }
            /* Make sure sidebar cards have enough space */
            .sidebar-card {
                margin-bottom: 20px;
            }
        </style>
        <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    """, unsafe_allow_html=True)

def create_sidebar_info(network_type):
    """Create standard sidebar information panels"""
    # About Network Analysis
    st.sidebar.markdown("""
    <div class="sidebar-card" style="background-color: #f5f5f5; padding: 15px; border-radius: 8px;">
        <h4 style="margin-top: 0; color: #333;">About Network Analysis</h4>
        <p style="font-size: 0.9em; color: #555;">These visualizations use bibliometric analysis techniques to reveal patterns in research data, helping identify key actors, trends, and relationships in the scientific literature.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # About This Network
    st.sidebar.markdown(f"""
    <div class="sidebar-card" style="background-color: #f5f5f5; padding: 15px; border-radius: 8px; margin-top: 15px;">
        <h4 style="margin-top: 0; color: #333;">About This Network</h4>
        <p style="font-size: 0.9em; color: #555;">This is a {network_type} visualization that helps you understand relationships between research entities.</p>
        <p style="font-size: 0.85em; color: #666; margin-bottom: 0;">The nodes represent individual entities, and links show connections through shared citations or collaborations.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Interactive Guide
    st.sidebar.markdown("""
    <div class="sidebar-card" style="background: linear-gradient(135deg, #6e8efb, #a777e3); 
                border-radius: 8px; 
                padding: 15px; 
                color: white; 
                margin-top: 15px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h4 style="margin-top: 0; color: white; font-weight: 600;">📊 Interactive Guide</h4>
        <ul style="list-style-type: none; padding-left: 5px; margin-bottom: 0;">
            <li style="margin-bottom: 8px; display: flex; align-items: center;">
                <div style="background-color: rgba(255,255,255,0.3); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 8px;">⚙️</div>
                Click "<b>Show control panel</b>" in top-left
            </li>
            <li style="margin-bottom: 8px; display: flex; align-items: center;">
                <div style="background-color: rgba(255,255,255,0.3); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 8px;">🔍</div>
                Zoom with mouse wheel
            </li>
            <li style="margin-bottom: 8px; display: flex; align-items: center;">
                <div style="background-color: rgba(255,255,255,0.3); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 8px;">✋</div>
                Click and drag to pan
            </li>
            <li style="margin-bottom: 8px; display: flex; align-items: center;">
                <div style="background-color: rgba(255,255,255,0.3); border-radius: 50%; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; margin-right: 8px;">👆</div>
                Click nodes for details
            </li>
        </ul>
        <div style="background-color: rgba(255,255,255,0.2); border-radius: 5px; padding: 8px; margin-top: 10px; font-size: 0.85em;">
            <b>💡 Pro Tip:</b> Adjust colors, sizes, and labels to highlight different patterns
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_vosviewer(url):
    """Display VOSviewer visualization with the given URL"""
    vosviewer_html = f"""
    <div class="vosviewer-container">
        <div style="width:100%; height:85vh; min-height:500px;">
            <object
                type="text/html"
                data="{url}&simple_ui=true"
                style="width:100%; height:100%;">
            </object>
        </div>
    </div>
    """
    
    # Display the VOSviewer visualization
    components.html(
        vosviewer_html,
        height=800,
        scrolling=True
    )
    
    # Add footer with citation info
    st.markdown("""
    <div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 20px; text-align: center; font-size: 0.8em; color: #6c757d;">
        These visualizations were created with <a href="https://www.vosviewer.com/" target="_blank">VOSviewer</a>, a software tool for constructing and visualizing bibliometric networks.
    </div>
    """, unsafe_allow_html=True)