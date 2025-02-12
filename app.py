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

    # **Processing the uploaded file**
    if uploaded_file is not None:
        if analysis_type == "Basic Analysis":
            process_uploaded_file(uploaded_file, title, keywords, view_type, colormap)
        elif analysis_type == "Advanced Meta-Analysis":
            process_meta_analysis(uploaded_file, correction_method, p_threshold, view_type, colormap)

def process_uploaded_file(uploaded_file, title, keywords, view_type, colormap):
    """Process and display uploaded file"""
    try:
        # Load and validate data
        nifti_data = validate_nifti(uploaded_file)
        processed_data = process_vbm_data(nifti_data)

        # Create visualization
        col1, col2 = st.columns([2, 1])

        with col1:
            st.subheader("Brain Visualization")
            fig = create_brain_visualization(
                processed_data,
                view_type=view_type,
                colormap=colormap
            )
            st.pyplot(fig)

        with col2:
            st.subheader("Statistics")
            stats_report = generate_statistics_report(processed_data)
            st.write(stats_report)

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def process_meta_analysis(uploaded_file, correction_method, p_threshold, view_type, colormap):
    """Process advanced meta-analysis"""
    try:
        # Load and validate data
        nifti_data = validate_nifti(uploaded_file)
        
        # Perform ALE analysis
        ale_results = perform_ale_analysis([nifti_data], p_threshold=p_threshold)
        
        # Apply cluster correction if selected
        if correction_method in ['FWE', 'FDR']:
            ale_results = apply_cluster_correction(
                ale_results, 
                method=correction_method.lower(),
                p_threshold=p_threshold
            )
        
        # Create visualization
        processed_nifti = nib.Nifti1Image(ale_results, nifti_data.affine)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Meta-Analysis Results")
            fig = create_brain_visualization(
                processed_nifti,
                view_type=view_type,
                colormap=colormap
            )
            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error in meta-analysis: {str(e)}")

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
                    if results:
                        display_pubmed_results(results)
                    else:
                        st.warning("No PubMed results found.")
                except Exception as e:
                    st.error(f"Error searching PubMed: {str(e)}")

    with col2:
        if st.button("Search NeuroVault"):
            if search_query:
                try:
                    results = search_neurovault(search_query)
                    if results:
                        display_neurovault_results(results)
                    else:
                        st.warning("No NeuroVault results found.")
                except Exception as e:
                    st.error(f"Error searching NeuroVault: {str(e)}")

def display_pubmed_results(results):
    """Display PubMed search results"""
    st.subheader("PubMed Results")
    for result in results:
        with st.expander(f"{result['title']} ({result['year']})"):
            st.write(f"Authors: {result['authors']}")
            st.write(f"Journal: {result['journal']}")
            st.write(f"PMID: {result['pmid']}")
            pubmed_link = f"https://pubmed.ncbi.nlm.nih.gov/{result['pmid']}"
            st.markdown(f"[View on PubMed]({pubmed_link})")

def display_neurovault_results(results):
    """Display NeuroVault search results"""
    st.subheader("NeuroVault Results")
    for result in results:
        with st.expander(f"{result['title']}"):
            st.write(f"Map Type: {result['map_type']}")
            st.write(f"Cognitive Paradigm: {result['cognitive_paradigm_cogatlas']}")
            neurovault_link = f"https://neurovault.org/images/{result['id']}"
            st.markdown(f"[View on NeuroVault]({neurovault_link})")

def run_documentation_tab():
    """Display documentation"""
    st.header("📖 Documentation")
    st.write("See the documentation tab for full details.")

if __name__ == "__main__":
    main()
