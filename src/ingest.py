import os
import re
from pathlib import Path
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import SearchIndex, SimpleField, SearchableField
from pypdf import PdfReader
from pypdf.errors import PdfReadError, DependencyError
from config import SEARCH_ENDPOINT, SEARCH_KEY, INDEX_NAME

# 1️⃣ Create index if it doesn't exist
index_client = SearchIndexClient(endpoint=SEARCH_ENDPOINT, credential=AzureKeyCredential(SEARCH_KEY))

fields = [
    SimpleField(name="id", type="Edm.String", key=True),
    SearchableField(name="content", type="Edm.String"),
    SimpleField(name="source_file", type="Edm.String"),
    SimpleField(name="page_number", type="Edm.Int32"),
]

index = SearchIndex(name=INDEX_NAME, fields=fields)

try:
    index_client.create_index(index)
    print("Index created")
except Exception:
    print("Index already exists")

# 2️⃣ Connect to search index
search_client = SearchClient(endpoint=SEARCH_ENDPOINT, index_name=INDEX_NAME, credential=AzureKeyCredential(SEARCH_KEY))

# 3️⃣ Loop through all PDFs in folder
docs_path = Path("data/documents")

for file in docs_path.iterdir():
    if file.suffix.lower() != ".pdf":
        continue

    try:
        reader = PdfReader(str(file))
    except (PdfReadError, DependencyError) as e:
        print(f"Skipping {file.name} (unreadable): {e}")
        continue

    for i, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text()
        except Exception as e:
            print(f"Skipping page {i} of {file.name}: {e}")
            continue

        if not text:
            continue

        # Sanitize filename for valid Azure key
        sanitized_name = re.sub(r'[^a-zA-Z0-9_\-]', '_', file.stem)

        doc = {
            "id": f"{sanitized_name}_page_{i}",
            "content": text,
            "source_file": file.name,
            "page_number": i
        }

        try:
            search_client.upload_documents([doc])
            print(f"Uploaded {file.name}, page {i}")
        except Exception as e:
            print(f"Failed to upload page {i} of {file.name}: {e}")
