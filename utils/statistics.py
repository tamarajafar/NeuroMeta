import numpy as np
import pandas as pd

def generate_statistics_report(nifti_data):
    """
    Generate basic statistical report for the brain data
    """
    try:
        # Get data array
        data_array = nifti_data.get_fdata()
        
        # Calculate basic statistics
        stats = {
            "Mean Intensity": np.mean(data_array),
            "Standard Deviation": np.std(data_array),
            "Maximum Value": np.max(data_array),
            "Minimum Value": np.min(data_array),
            "Number of Non-zero Voxels": np.count_nonzero(data_array),
            "Total Volume (voxels)": data_array.size,
            "Percent Active Voxels": (np.count_nonzero(data_array) / data_array.size) * 100
        }
        
        # Create DataFrame for better display
        stats_df = pd.DataFrame.from_dict(stats, orient='index', columns=['Value'])
        stats_df['Value'] = stats_df['Value'].round(4)
        
        # Calculate basic cluster statistics
        clusters = identify_clusters(data_array)
        cluster_stats = {
            "Number of Clusters": len(clusters),
            "Largest Cluster Size": max([len(c) for c in clusters]) if clusters else 0,
            "Average Cluster Size": np.mean([len(c) for c in clusters]) if clusters else 0
        }
        
        cluster_df = pd.DataFrame.from_dict(cluster_stats, orient='index', columns=['Value'])
        cluster_df['Value'] = cluster_df['Value'].round(4)
        
        # Combine statistics
        final_stats = pd.concat([stats_df, cluster_df])
        
        return final_stats
        
    except Exception as e:
        raise ValueError(f"Error generating statistics: {str(e)}")

def identify_clusters(data_array, threshold=0.5):
    """
    Identify clusters in the brain data
    """
    try:
        # Threshold the data
        binary_data = data_array > threshold
        
        # Label connected components
        from scipy import ndimage
        labeled_array, num_features = ndimage.label(binary_data)
        
        # Extract clusters
        clusters = []
        for label in range(1, num_features + 1):
            cluster = np.where(labeled_array == label)
            clusters.append(cluster)
            
        return clusters
        
    except Exception as e:
        raise ValueError(f"Error identifying clusters: {str(e)}")
