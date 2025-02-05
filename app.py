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

def save_analysis(file_data, title, keywords):
    """Save analysis results to database"""
    db = SessionLocal()
    try:
        study = Study(
            title=title,
            keywords=keywords,
            created_at=datetime.utcnow()
        )
        db.add(study)
        db.flush()

        brain_map = BrainMap(
            study_id=study.id,
            map_type='vbm',
            data=file_data.read(),
            created_at=datetime.utcnow()
        )
        db.add(brain_map)
        db.commit()
        return study.id
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()

def load_analysis(study_id):
    """Load analysis from database"""
    db = SessionLocal()
    try:
        brain_map = db.query(BrainMap).filter(BrainMap.study_id == study_id).first()
        if brain_map:
            return io.BytesIO(brain_map.data)
        return None
    finally:
        db.close()

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
    # Sidebar controls
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
    
# Add footer with author information
    st.sidebar.markdown("---")
    st.sidebar.markdown("Built by Tamara Jafar")
    st.sidebar.markdown("Contact Me at tjafar@usc.edu")
    st.sidebar.markdown("Follow me on [Twitter ⭐](https://x.com/TamaraJafar)!")

    if uploaded_file is not None:
        if analysis_type == "Basic Analysis":
            process_uploaded_file(uploaded_file, title, keywords, view_type, colormap)
        else:
            process_meta_analysis(uploaded_file, correction_method, p_threshold, view_type, colormap)

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
        
        with col2:
            st.subheader("Analysis Details")
            st.write(f"Correction Method: {correction_method}")
            st.write(f"P-threshold: {p_threshold}")
            
            if st.button("Download Results"):
                # Save results to NIfTI file
                output = io.BytesIO()
                nib.save(processed_nifti, output)
                b64 = base64.b64encode(output.getvalue()).decode()
                href = f'<a href="data:application/x-nifti;base64,{b64}" download="meta_analysis_results.nii.gz">Download NIfTI Results</a>'
                st.markdown(href, unsafe_allow_html=True)
                
    except Exception as e:
        st.error(f"Error in meta-analysis: {str(e)}")
    else:
        show_welcome_message()

def run_literature_search_tab():
    """Literature search functionality"""
    st.header("Literature Search")

    # Search interface
    search_query = st.text_input("Enter search terms:")
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Search PubMed"):
            if search_query:
                try:
                    results = search_pubmed(search_query)
                    st.session_state.pubmed_results = results
                    display_pubmed_results(results)
                except Exception as e:
                    st.error(f"Error searching PubMed: {str(e)}")

    with col2:
        if st.button("Search NeuroVault"):
            if search_query:
                try:
                    results = search_neurovault(search_query)
                    st.session_state.neurovault_results = results
                    display_neurovault_results(results)
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
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button(f"Visualize Map {result['id']}", key=f"viz_{result['id']}"):
                    try:
                        # Download and process the map
                        temp_file = download_neurovault_map(result['file_url'])
                        nifti_data = nib.load(temp_file)
                        processed_data = process_vbm_data(nifti_data)

                        # Create and display visualization
                        fig = create_brain_visualization(processed_data)
                        st.pyplot(fig)

                        # Clean up
                        os.unlink(temp_file)
                    except Exception as e:
                        st.error(f"Error processing brain map: {str(e)}")
            
            with col2:
                neurovault_link = f"https://neurovault.org/images/{result['id']}"
                st.markdown(f"[View on NeuroVault]({neurovault_link})")
                download_link = result['file_url']
                st.markdown(f"[Download Map]({download_link})")

def process_uploaded_file(uploaded_file, title, keywords, view_type, colormap):
    """Process and display uploaded file"""
    try:
        # Save analysis to database
        if st.sidebar.button("Save Analysis"):
            if title and keywords:
                study_id = save_analysis(uploaded_file, title, keywords)
                st.success(f"Analysis saved successfully! Study ID: {study_id}")
            else:
                st.warning("Please provide title and keywords to save the analysis")

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

            # Download buttons
            if st.button("Download Statistics Report"):
                report_str = str(stats_report)
                b64 = base64.b64encode(report_str.encode()).decode()
                href = f'<a href="data:text/plain;base64,{b64}" download="stats_report.txt">Download Report</a>'
                st.markdown(href, unsafe_allow_html=True)

            if st.button("Download Visualization"):
                buf = io.BytesIO()
                fig.savefig(buf, format='png')
                buf.seek(0)
                b64 = base64.b64encode(buf.getvalue()).decode()
                href = f'<a href="data:image/png;base64,{b64}" download="brain_visualization.png">Download Visualization</a>'
                st.markdown(href, unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error processing file: {str(e)}")

def run_documentation_tab():
    """Display documentation and instructions"""
    st.header("Documentation")
    
st.subheader("NeuroMeta: A VBM/ALE Meta-Analysis Viewer")

st.write("""
NeuroMeta is a **Voxel-Based Morphometry (VBM)** and **Activation Likelihood Estimation (ALE) Meta-Analysis Viewer** web application designed for neuroscience researchers to analyze and visualize neuroimaging data.  
""")

# Features Section
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

# Installation Section
with st.expander("Installation"):
    st.markdown("""
    **The application requires the following dependencies:**
    ```bash
    pip install streamlit nibabel nilearn numpy pandas scipy sqlalchemy matplotlib biopython requests
    ```
    """)

# Usage Guide
with st.expander("Usage Guide"):
    st.markdown("""
    ### Basic Analysis
    1. Open the application in your browser
    2. Select **"Basic Analysis"** from the Analysis Type dropdown
    3. Upload your **NIfTI file** (.nii or .nii.gz)
    4. Enter study information:
       - Study Title
       - Keywords
    5. Customize visualization:
       - View type (Ortho/Sagittal/Coronal/Axial)
       - Color scheme
    6. View results and statistics
    7. Download visualization or statistics report

    ### Advanced Meta-Analysis
    1. Select **"Advanced Meta-Analysis"** from Analysis Type
    2. Choose correction method:
       - None
       - **FWE** (Family-Wise Error)
       - **FDR** (False Discovery Rate)
    3. Set **p-value threshold** (0.01-0.10)
    4. Upload **NIfTI file**
    5. View results:
       - Brain visualization
       - Analysis details
    6. Download results

    ### Literature Search
    1. Configure **API email** (required for first use)
    2. Enter **search terms**
    3. Choose search type:
       - **PubMed:** For academic papers
       - **NeuroVault:** For brain maps
    4. View and interact with results
    5. Download or visualize related data
    """)

# Technical Documentation
with st.expander("Technical Documentation"):
    st.markdown("""
    ### Core Modules
    - **app.py**: Manages user interface, file processing, and visualization
    - **utils/meta_analysis.py**: Implements ALE analysis, statistical thresholding
    - **utils/visualization.py**: Handles brain map visualization (View types, colormap customization)
    - **utils/statistics.py**: Provides statistical analysis (Basic stats, cluster identification)
    - **utils/api_integration.py**: Manages external API connections (PubMed, NeuroVault)
    - **database.py**: Handles SQLite database storage and session management

    ### Data Flow
    1. User uploads **NIfTI file**
    2. **Data validation** and **preprocessing**
    3. **Analysis** (Basic or Meta)
    4. **Results generation**
    5. **Visualization**
    6. **Optional:** Save results in the database
    """)

# Troubleshooting Section
with st.expander("Troubleshooting"):
    st.markdown("""
    ### Common Issues
    **1. File Upload Errors**
    - Ensure file is in **.nii or .nii.gz** format
    - Check **file size** (max 200MB)

    **2. Analysis Failures**
    - Verify **data format**
    - Check **p-value threshold** settings
    - Ensure **sufficient data points**

    **3. API Connection Issues**
    - Configure **email** in settings
    - Check **internet connection**
    - Verify **API access**

    **4. Visualization Problems**
    - Try different **view types**
    - Adjust **colormap settings**
    - Clear **browser cache**
    
    ### Need Help?
    Contact me: **tjafar@usc.edu**
    """)

def show_welcome_message():
    """Display welcome message and instructions"""

    st.info("Please upload a NIfTI file to begin analysis")

    st.subheader("Example Analysis")
    st.write("""
    This tool allows you to:
    1. Upload VBM/ALE meta-analysis data
    2. Visualize brain maps with interactive controls
    3. Generate statistical reports
    4. Download results and visualizations
    5. Save analyses to database for future reference
    6. Search and integrate with PubMed and NeuroVault
    """)

if __name__ == "__main__":
    main()
