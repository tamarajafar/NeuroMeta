import matplotlib.pyplot as plt
from nilearn import plotting
import numpy as np

def create_brain_visualization(nifti_data, view_type='ortho', colormap='hot'):
    """
    Create brain visualization using Nilearn
    """
    try:
        # Set up the backend
        plt.switch_backend('agg')

        # Clear any existing plots
        plt.close('all')

        # Create figure with specific size
        fig = plt.figure(figsize=(12, 8))

        # Set up display parameters
        display_params = {
            'cmap': colormap,
            'colorbar': True,
            'cut_coords': 5,
            'black_bg': False,
            'figure': fig
        }

        # Create visualization based on view type
        if view_type == 'ortho':
            plotting.plot_stat_map(
                nifti_data,
                display_mode='ortho',
                **display_params
            )
        elif view_type == 'sagittal':
            plotting.plot_stat_map(
                nifti_data,
                display_mode='x',
                **display_params
            )
        elif view_type == 'coronal':
            plotting.plot_stat_map(
                nifti_data,
                display_mode='y',
                **display_params
            )
        elif view_type == 'axial':
            plotting.plot_stat_map(
                nifti_data,
                display_mode='z',
                **display_params
            )

        # Add title
        plt.title(f"Brain Visualization - {view_type.capitalize()} View")

        # Tight layout to prevent cutting off
        plt.tight_layout()

        return fig

    except Exception as e:
        plt.close('all')  # Clean up on error
        raise ValueError(f"Error creating visualization: {str(e)}")