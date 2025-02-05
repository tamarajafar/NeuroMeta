from Bio import Entrez
import requests
import json
import tempfile
import os

# Configure email for PubMed API
Entrez.email = "your.email@example.com"  # Will be replaced with user's email

class APIConfig:
    NEUROVAULT_BASE_URL = "https://neurovault.org/api"
    PUBMED_BATCH_SIZE = 100

def search_pubmed(query, max_results=20):
    """
    Search PubMed for neuroimaging studies
    """
    try:
        # Search PubMed
        handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
        results = Entrez.read(handle)
        handle.close()

        if not results['IdList']:
            return []

        # Fetch details for found articles
        handle = Entrez.efetch(db="pubmed", id=results['IdList'], rettype="medline", retmode="xml")
        records = Entrez.read(handle)
        handle.close()

        return [{
            'pmid': record['MedlineCitation']['PMID'],
            'title': record['MedlineCitation']['Article']['ArticleTitle'],
            'authors': record['MedlineCitation']['Article']['AuthorList'][0]['LastName'] if 'AuthorList' in record['MedlineCitation']['Article'] else 'N/A',
            'year': record['MedlineCitation']['Article']['Journal']['JournalIssue']['PubDate'].get('Year', 'N/A'),
            'journal': record['MedlineCitation']['Article']['Journal']['Title']
        } for record in records['PubmedArticle']]

    except Exception as e:
        raise ValueError(f"Error searching PubMed: {str(e)}")

def search_neurovault(query):
    """
    Search NeuroVault for brain maps
    """
    try:
        response = requests.get(
            f"{APIConfig.NEUROVAULT_BASE_URL}/images/",
            params={'name__icontains': query},
            timeout=10
        )
        response.raise_for_status()
        
        results = response.json()
        return [{
            'id': item['id'],
            'title': item['name'],
            'collection_id': item['collection_id'],
            'file_url': item['file'],
            'map_type': item['map_type'],
            'cognitive_paradigm_cogatlas': item.get('cognitive_paradigm_cogatlas', 'N/A')
        } for item in results['results']]

    except Exception as e:
        raise ValueError(f"Error searching NeuroVault: {str(e)}")

def download_neurovault_map(file_url):
    """
    Download a brain map from NeuroVault
    """
    try:
        response = requests.get(file_url, timeout=30, stream=True)
        response.raise_for_status()
        
        # Create temporary file
        suffix = '.nii.gz'
        temp_dir = tempfile.mkdtemp()
        temp_path = os.path.join(temp_dir, f"map{suffix}")
        
        with open(temp_path, 'wb') as tmp_file:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    tmp_file.write(chunk)
        
        return temp_path

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error downloading from NeuroVault: {str(e)}")
    except Exception as e:
        raise ValueError(f"Error processing downloaded map: {str(e)}")

def configure_email(email):
    """
    Configure email for PubMed API
    """
    Entrez.email = email
