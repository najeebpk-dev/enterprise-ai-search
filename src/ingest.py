"""
PDF Document Ingestion Pipeline with Vector Embeddings

This module ingests PDF documents from the data/documents folder,
extracts text content, generates embeddings using Azure OpenAI,
and uploads the documents to Azure Cognitive Search.
"""

import os
import re
import logging
from pathlib import Path
from typing import List, Dict, Any
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, 
    SimpleField, 
    SearchableField,
    SearchField,
    SearchFieldDataType,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchProfile
)
from pypdf import PdfReader
from pypdf.errors import PdfReadError
from openai import AzureOpenAI
from tqdm import tqdm
from config import (
    SEARCH_ENDPOINT, 
    SEARCH_KEY, 
    INDEX_NAME,
    OPENAI_ENDPOINT,
    OPENAI_KEY,
    EMBEDDING_MODEL
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Batch size for uploading documents
BATCH_SIZE = 50


def validate_config():
    """Validate that all required configuration variables are set."""
    required_vars = {
        'SEARCH_ENDPOINT': SEARCH_ENDPOINT,
        'SEARCH_KEY': SEARCH_KEY,
        'INDEX_NAME': INDEX_NAME,
        'OPENAI_ENDPOINT': OPENAI_ENDPOINT,
        'OPENAI_KEY': OPENAI_KEY,
        'EMBEDDING_MODEL': EMBEDDING_MODEL
    }
    
    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")
    
    logger.info("✓ Configuration validated successfully")


def create_or_update_index(index_client: SearchIndexClient) -> None:
    """
    Create or update the search index with vector search capabilities.
    
    Args:
        index_client: Azure Search Index Client
    """
    # Define the search index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String, analyzer_name="en.microsoft"),
        SimpleField(name="source_file", type=SearchFieldDataType.String, filterable=True, facetable=True),
        SimpleField(name="page_number", type=SearchFieldDataType.Int32, filterable=True, sortable=True),
        SearchField(
            name="embedding",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,  # text-embedding-ada-002 dimension
            vector_search_profile_name="vector-profile"
        ),
    ]
    
    # Configure vector search with HNSW algorithm
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                parameters={
                    "m": 4,
                    "efConstruction": 400,
                    "efSearch": 500,
                    "metric": "cosine"
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="vector-profile",
                algorithm_configuration_name="hnsw-config"
            )
        ]
    )
    
    # Create the search index
    index = SearchIndex(
        name=INDEX_NAME,
        fields=fields,
        vector_search=vector_search
    )
    
    try:
        index_client.create_or_update_index(index)
        logger.info(f"✓ Index '{INDEX_NAME}' created/updated successfully with vector search")
    except Exception as e:
        logger.error(f"✗ Failed to create/update index: {e}")
        raise


def generate_embedding(text: str, openai_client: AzureOpenAI) -> List[float]:
    """
    Generate embedding vector for the given text using Azure OpenAI.
    
    Args:
        text: Input text to generate embedding for
        openai_client: Azure OpenAI client
        
    Returns:
        List of floats representing the embedding vector
    """
    try:
        # Truncate text if too long (max ~8000 tokens for ada-002)
        max_chars = 30000
        if len(text) > max_chars:
            text = text[:max_chars]
        
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[text]
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"✗ Failed to generate embedding: {e}")
        raise


def extract_pdf_content(file_path: Path) -> List[Dict[str, Any]]:
    """
    Extract text content from a PDF file, page by page.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        List of dictionaries containing page content and metadata
    """
    pages = []
    
    try:
        reader = PdfReader(str(file_path))
        
        for i, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text()
                
                # Skip empty pages
                if not text or len(text.strip()) < 50:
                    logger.warning(f"  ⚠ Skipping empty/short page {i}")
                    continue
                
                pages.append({
                    "page_number": i,
                    "content": text.strip()
                })
                
            except Exception as e:
                logger.warning(f"  ⚠ Failed to extract page {i}: {e}")
                continue
        
        logger.info(f"  ✓ Extracted {len(pages)} pages from {file_path.name}")
        return pages
        
    except PdfReadError as e:
        logger.error(f"  ✗ Cannot read PDF {file_path.name}: {e}")
        return []
    except Exception as e:
        logger.error(f"  ✗ Unexpected error reading {file_path.name}: {e}")
        return []


def process_and_upload_documents(
    docs_path: Path,
    search_client: SearchClient,
    openai_client: AzureOpenAI
) -> Dict[str, int]:
    """
    Process all PDF files in the documents folder and upload to Azure Search.
    
    Args:
        docs_path: Path to the documents folder
        search_client: Azure Search client
        openai_client: Azure OpenAI client
        
    Returns:
        Dictionary with statistics (files_processed, pages_uploaded, errors)
    """
    if not docs_path.exists():
        logger.error(f"✗ Documents folder not found: {docs_path}")
        return {"files_processed": 0, "pages_uploaded": 0, "errors": 0}
    
    pdf_files = list(docs_path.glob("*.pdf"))
    if not pdf_files:
        logger.warning(f"⚠ No PDF files found in {docs_path}")
        return {"files_processed": 0, "pages_uploaded": 0, "errors": 0}
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    stats = {
        "files_processed": 0,
        "pages_uploaded": 0,
        "errors": 0
    }
    
    batch = []
    
    for file in tqdm(pdf_files, desc="Processing PDFs", unit="file"):
        logger.info(f"\nProcessing: {file.name}")
        
        # Extract pages from PDF
        pages = extract_pdf_content(file)
        if not pages:
            stats["errors"] += 1
            continue
        
        stats["files_processed"] += 1
        
        # Sanitize filename for valid Azure document key
        sanitized_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', file.stem)
        
        # Process each page
        for page_data in tqdm(pages, desc=f"  Pages", leave=False):
            try:
                # Generate embedding for the page content
                embedding = generate_embedding(page_data["content"], openai_client)
                
                # Create document for upload
                doc = {
                    "id": f"{sanitized_name}_page_{page_data['page_number']}",
                    "content": page_data["content"],
                    "source_file": file.name,
                    "page_number": page_data["page_number"],
                    "embedding": embedding
                }
                
                batch.append(doc)
                
                # Upload in batches
                if len(batch) >= BATCH_SIZE:
                    try:
                        search_client.upload_documents(documents=batch)
                        stats["pages_uploaded"] += len(batch)
                        batch = []
                    except Exception as e:
                        logger.error(f"  ✗ Batch upload failed: {e}")
                        stats["errors"] += len(batch)
                        batch = []
                
            except Exception as e:
                logger.error(f"  ✗ Failed to process page {page_data['page_number']}: {e}")
                stats["errors"] += 1
    
    # Upload remaining documents in batch
    if batch:
        try:
            search_client.upload_documents(documents=batch)
            stats["pages_uploaded"] += len(batch)
        except Exception as e:
            logger.error(f"✗ Final batch upload failed: {e}")
            stats["errors"] += len(batch)
    
    return stats


def main():
    """Main ingestion pipeline."""
    logger.info("=" * 60)
    logger.info("ENTERPRISE AI SEARCH - DOCUMENT INGESTION PIPELINE")
    logger.info("=" * 60)
    
    try:
        # Validate configuration
        validate_config()
        
        # Initialize Azure clients
        logger.info("\nInitializing Azure clients...")
        index_client = SearchIndexClient(
            endpoint=SEARCH_ENDPOINT,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
        
        search_client = SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
        
        openai_client = AzureOpenAI(
            api_key=OPENAI_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=OPENAI_ENDPOINT
        )
        
        logger.info("✓ Azure clients initialized")
        
        # Create or update search index
        logger.info("\nSetting up search index...")
        create_or_update_index(index_client)
        
        # Process and upload documents
        logger.info("\nStarting document ingestion...")
        docs_path = Path("data/documents")
        stats = process_and_upload_documents(docs_path, search_client, openai_client)
        
        # Print summary
        logger.info("\n" + "=" * 60)
        logger.info("INGESTION COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Files processed: {stats['files_processed']}")
        logger.info(f"Pages uploaded: {stats['pages_uploaded']}")
        logger.info(f"Errors: {stats['errors']}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"\n✗ Ingestion failed: {e}")
        raise


if __name__ == "__main__":
    main()
