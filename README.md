# NeuroMeta: A VBM/ALE Meta-Analysis Viewer
NeuroMeta is a Voxel-Based Morphometry (VBM) and Activation Likelihood Estimation (ALE) Meta-Analysis Viewer web application designed for neuroscience researchers to analyze and visualize neuroimaging data.  

## Documentation and User Manual

### Table of Contents
1. Introduction
2. Features
3. Installation
4. Usage Guide
5. Technical Documentation
6. Troubleshooting

## 1. Introduction
NeuroMeta is a powerful web application designed for neuroscience researchers to analyze and visualize brain imaging data. It supports both Voxel-Based Morphometry (VBM) and Activation Likelihood Estimation (ALE) meta-analyses.

## 2. Features
- Basic Analysis
  - VBM data visualization
  - Statistical analysis
  - Multiple view types (ortho, sagittal, coronal, axial)
  - Customizable colormaps
  
- Advanced Meta-Analysis
  - ALE analysis support
  - Cluster-level corrections (Family-Wise Error, False Discovery Rate)
  - P-value thresholding
  - Results visualization and download

- Literature Integration
  - PubMed search integration
  - NeuroVault database access
  - Study information management

## 3. Installation
The application requires the following dependencies:
- streamlit
- nibabel
- nilearn
- numpy
- pandas
- scipy
- sqlalchemy
- matplotlib
- biopython
- requests

## 4. Usage Guide

### Basic Analysis
1. Open the application in your browser
2. Select "Basic Analysis" from the Analysis Type dropdown
3. Upload your NIfTI file (.nii or .nii.gz)
4. Enter study information:
   - Study Title
   - Keywords
5. Customize visualization:
   - View type (ortho/sagittal/coronal/axial)
   - Color scheme
6. View results and statistics
7. Download visualization or statistics report

### Advanced Meta-Analysis
1. Select "Advanced Meta-Analysis" from Analysis Type
2. Choose correction method:
   - None
   - FWE (Family-Wise Error)
   - FDR (False Discovery Rate)
3. Set p-value threshold (0.01-0.10)
4. Upload NIfTI file
5. View results:
   - Brain visualization
   - Analysis details
6. Download results

### Literature Search
1. Configure API email (required for first use)
2. Enter search terms
3. Choose search type:
   - PubMed: For academic papers
   - NeuroVault: For brain maps
4. View and interact with results
5. Download or visualize related data

## 5. Technical Documentation

### Core Modules

#### app.py
Main application file handling:
- User interface
- Workflow management
- File processing
- Results visualization

#### utils/meta_analysis.py
Implements advanced statistical analysis:
- ALE analysis
- Cluster-level corrections
- Statistical thresholding

#### utils/visualization.py
Handles brain map visualization:
- Multiple view types
- Colormap customization
- Figure generation

#### utils/statistics.py
Provides statistical analysis:
- Basic statistics
- Cluster identification
- Report generation

#### utils/api_integration.py
Manages external API connections:
- PubMed integration
- NeuroVault access
- Data retrieval

#### database.py
Handles data persistence:
- SQLite database management
- Session handling
- Study/map storage

### Data Flow
1. User uploads NIfTI file
2. Data validation and preprocessing
3. Analysis (Basic/Meta)
4. Results generation
5. Visualization
6. Optional: Database storage

## 6. Troubleshooting

### Common Issues

1. File Upload Errors
- Solution: Ensure file is in .nii or .nii.gz format
- Check file size (max 200MB)

2. Analysis Failures
- Solution: Verify data format
- Check p-value threshold settings
- Ensure sufficient data points

3. API Connection Issues
- Solution: Configure email in settings
- Check internet connection
- Verify API access

4. Visualization Problems
- Solution: Try different view types
- Adjust colormap settings
- Clear browser cache

### Support
For technical issues:
1. Check error messages
2. Review documentation
3. Contact me @ tjafar@usc.edu

