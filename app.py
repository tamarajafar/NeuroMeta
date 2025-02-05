import streamlit as st
import nibabel as nib
import numpy as np
from utils.data_processing import validate_nifti, process_vbm_data
from utils.visualization import create_brain_visualization
from utils.statistics import generate_statistics_report
from utils.api_integration import search_pubmed, search_neurovault, download_neurovault_map, configure_email
from utils.meta_analysis import perform_ale_analysis, apply_cluster_correction
import io
import base64
from database import init_db, SessionLocal
from models import Study, BrainMap
from datetime import datetime
import json
import os

# Initialize database
init_db()

# Page configuration
st.set_page_config(
    page_title="VBM/ALE Meta-Analysis Viewer",
    page_icon="🧠",
    layout="wide"
)

# Initialize session state for email configuration
if 'email_configured' not in st.session_state:
    st.session_state.email_configured = False

def configure_api_email():
    """Configure email for API access"""
    if not st.session_state.email_configured:
        with st.sidebar.expander("⚙️ API Configuration"):
            email = st.text_input("Enter your email for API access:")
            if email and st.button("Save"):
                configure_email(email)
                st.session_state.email_configured = True
                st.success("Email configured successfully!")

def main():
    st.title("🧠 NeuroMeta: VBM/ALE Meta-Analysis Viewer")
    
    # Configure API email
    configure_api_email()
    
    # Create tabs for different functionalities
    tab1, tab2, tab3 = st.tabs(["Analysis", "Literature Search", "Documentation"])
    
    with tab1:
        run_analysis_tab()
    
    with tab2:
        if st.session_state.email_configured:
            run_literature_search_tab()
        else:
            st.warning("Please configure your email in the sidebar to use the literature search feature.")
    
    with tab3:
        run_documentation_tab()

def run_analysis_tab():
    """Main analysis functionality"""
    st.sidebar.header("Analysis Controls")
    
    # Analysis type selection
    analysis_type = st.sidebar.selectbox(
        "Analysis Type",
        ["Basic Analysis", "Advanced Meta-Analysis"]
    )
    
    if analysis_type == "Advanced Meta-Analysis":
        correction_method = st.sidebar.selectbox(
            "Correction Method",
            ["None", "FWE", "FDR"]
        )
        p_threshold = st.sidebar.slider(
            "P-value threshold",
            0.01, 0.10, 0.05, 0.01
        )

    uploaded_file = st.sidebar.file_uploader(
        "Upload NIfTI file (.nii or .nii.gz)",
        type=['nii', 'nii.gz']
    )

    # Study information
    title = st.sidebar.text_input("Study Title")
    keywords = st.sidebar.text_input("Keywords (comma-separated)")

    # Visualization options
    st.sidebar.subheader("Visualization Options")
    view_type = st.sidebar.selectbox(
        "Select view type",
        ["ortho", "sagittal", "coronal", "axial"]
    )
    
    colormap = st.sidebar.selectbox(
        "Color scheme",
        ["hot", "cold", "RdBu_r", "YlOrRd"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built by Tamara Jafar")
    st.sidebar.markdown("Contact Me at tjafar@usc.edu")
    st.sidebar.markdown("Follow me on [Twitter ⭐](https://x.com/TamaraJafar)!")

def run_literature_search_tab():
    """Literature search functionality"""
    st.header("Literature Search")
    search_query = st.text_input("Enter search terms:")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Search PubMed"):
            if search_query:
                try:
                    results = search_pubmed(search_query)
                    display_pubmed_results(results)
                except Exception as e:
                    st.error(f"Error searching PubMed: {str(e)}")

    with col2:
        if st.button("Search NeuroVault"):
            if search_query:
                try:
                    results = search_neurovault(search_query)
                    display_neurovault_results(results)
                except Exception as e:
                    st.error(f"Error searching NeuroVault: {str(e)}")

def run_documentation_tab():
    """Display documentation and instructions"""
    st.header("📖 Documentation")
    
    with st.expander("Features", expanded=True):
        st.markdown("""
        ### Basic Analysis
        - VBM data visualization
        - Statistical analysis
        - Multiple view types (Ortho, Sagittal, Coronal, Axial)
        - Customizable colormaps

        ### Advanced Meta-Analysis
        - ALE analysis support
        - Cluster-level corrections (FWE, FDR)
        - P-value thresholding
        - Results visualization and download

        ### Literature Integration
        - PubMed search integration
        - NeuroVault database access
        - Study information management
        """)

    with st.expander("Installation"):
        st.markdown("""
        **The application requires the following dependencies:**
        ```bash
        pip install streamlit nibabel nilearn numpy pandas scipy sqlalchemy matplotlib biopython requests
        ```
        """)
    
    with st.expander("Usage Guide"):
        st.markdown("""
        ### Basic Analysis
        1. Open the application in your browser
        2. Select "Basic Analysis" from the dropdown
        3. Upload your NIfTI file (.nii or .nii.gz)
        4. Enter study information
        5. Customize visualization
        6. View and download results
        """)
    
    with st.expander("Technical Documentation"):
        st.markdown("""
        ### Core Modules
        - **app.py**: Manages user interface and processing
        - **utils/meta_analysis.py**: Implements ALE analysis
        - **utils/visualization.py**: Handles visualization
        - **database.py**: Manages SQLite storage
        """)
    
    with st.expander("Troubleshooting"):
        st.markdown("""
        ### Common Issues
        - **File Upload Errors**: Ensure correct format and size
        - **Analysis Failures**: Check p-value and data format
        - **API Connection Issues**: Configure email settings
        """)

if __name__ == "__main__":
    main()
