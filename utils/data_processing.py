import nibabel as nib
import numpy as np
from scipy import ndimage
import io
import os
import tempfile

def validate_nifti(file_upload):
    """
    Validate and load NIfTI file
    """
    try:
        # Create a temporary file to save the upload
        suffix = '.nii.gz' if file_upload.name.endswith('.gz') else '.nii'
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp_file:
            # Write uploaded file content to temporary file
            tmp_file.write(file_upload.getvalue())
            tmp_file.flush()

            # Load NIfTI file from temporary file path
            nifti_data = nib.load(tmp_file.name)

            # Basic validation
            if len(nifti_data.shape) < 3:
                raise ValueError("Invalid dimensions: Expected 3D or 4D data")

            # Load the data into memory before closing the file
            nifti_data = nib.Nifti1Image(nifti_data.get_fdata(), nifti_data.affine)

        # Clean up temporary file
        os.unlink(tmp_file.name)
        return nifti_data

    except Exception as e:
        raise ValueError(f"Invalid NIfTI file: {str(e)}")

def process_vbm_data(nifti_data):
    """
    Process VBM/ALE data for visualization
    """
    try:
        # Get data array
        data_array = nifti_data.get_fdata()

        # Handle 4D data (take first volume if multiple volumes exist)
        if len(data_array.shape) > 3:
            data_array = data_array[:,:,:,0]

        # Basic preprocessing
        # Normalize data
        data_array = (data_array - np.min(data_array)) / (np.max(data_array) - np.min(data_array))

        # Apply minimal smoothing
        data_array = ndimage.gaussian_filter(data_array, sigma=1.0)

        # Create processed NIfTI object
        processed_nifti = nib.Nifti1Image(data_array, nifti_data.affine)

        return processed_nifti

    except Exception as e:
        raise ValueError(f"Error processing data: {str(e)}")