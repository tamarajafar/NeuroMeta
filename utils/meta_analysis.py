
import numpy as np
from scipy import ndimage, stats
from nilearn.image import math_img
import nibabel as nib

def perform_ale_analysis(nifti_maps, fwe_correction=True, p_threshold=0.05):
    """
    Perform Activation Likelihood Estimation (ALE) meta-analysis
    """
    try:
        # Convert maps to common space and get data arrays
        data_arrays = [nimg.get_fdata() for nimg in nifti_maps]
        
        # Calculate ALE values
        ale_values = np.zeros_like(data_arrays[0])
        for data in data_arrays:
            # Gaussian smoothing for each map
            smoothed = ndimage.gaussian_filter(data, sigma=3.0)
            ale_values += smoothed
        
        # Normalize ALE values
        ale_values /= len(data_arrays)
        
        if fwe_correction:
            # Perform FWE correction
            null_distributions = []
            for _ in range(1000):  # 1000 permutations
                shuffled = np.random.permutation(data_arrays)
                null_ale = np.mean([ndimage.gaussian_filter(d, sigma=3.0) 
                                  for d in shuffled], axis=0)
                null_distributions.append(np.max(null_ale))
            
            # Calculate threshold
            threshold = np.percentile(null_distributions, (1 - p_threshold) * 100)
            ale_values[ale_values < threshold] = 0
            
        return ale_values
        
    except Exception as e:
        raise ValueError(f"Error in ALE analysis: {str(e)}")

def apply_cluster_correction(stat_map, method='fwe', p_threshold=0.05):
    """
    Apply cluster-level correction (FWE or FDR)
    """
    try:
        # Get connected components
        labeled_array, num_features = ndimage.label(stat_map > 0)
        cluster_sizes = [np.sum(labeled_array == i) for i in range(1, num_features + 1)]
        
        if method.lower() == 'fwe':
            # FWE correction
            size_threshold = np.percentile(cluster_sizes, (1 - p_threshold) * 100)
            for i, size in enumerate(cluster_sizes, 1):
                if size < size_threshold:
                    stat_map[labeled_array == i] = 0
                    
        elif method.lower() == 'fdr':
            # FDR correction
            p_values = [1 - stats.norm.cdf(size) for size in cluster_sizes]
            _, corrected_p = stats.fdrcorrection(p_values, alpha=p_threshold)
            
            for i, p in enumerate(corrected_p, 1):
                if p > p_threshold:
                    stat_map[labeled_array == i] = 0
                    
        return stat_map
        
    except Exception as e:
        raise ValueError(f"Error in cluster correction: {str(e)}")
