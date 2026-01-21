import os
import sys
import re
import uuid
from pathlib import Path
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI
from PyPDF2 import PdfReader

# =========================
# Load environment variables
# =========================
dotenv_path = Path(__file__).parent / ".env"
if not dotenv_path.exists():
    print(f"❌ .env file not found at {dotenv_path}")
    sys.exit(1)

load_dotenv(dotenv_path)
print("✅ Environment variables loaded.")

# =========================
# Required environment vars
# =========================
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = os.getenv("INDEX_NAME")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-01")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")
DOCS_FOLDER = os.getenv("DOCS_FOLDER")

# Validate critical env vars
missing = []
for var_name, var_val in [
    ("SEARCH_ENDPOINT", SEARCH_ENDPOINT),
    ("SEARCH_KEY", SEARCH_KEY),
    ("INDEX_NAME", INDEX_NAME),
    ("OPENAI_API_ENDPOINT", OPENAI_API_ENDPOINT),
    ("OPENAI_API_KEY", OPENAI_API_KEY),
    ("EMBEDDING_MODEL", EMBEDDING_MODEL),
    ("DOCS_FOLDER", DOCS_FOLDER),
]:
    if not var_val:
        missing.append(var_name)
if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
    sys.exit(1)

# =========================
# Verify document folder
# =========================
docs_path = Path(DOCS_FOLDER)
if not docs_path.exists() or not docs_path.is_dir():
    print(f"❌ Folder not found: {DOCS_FOLDER}")
    sys.exit(1)

# =========================
# Initialize Azure Search Client
# =========================
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY),
)
print("✅ Azure Search client initialized.")

# =========================
# Initialize OpenAI Client
# =========================
openai_client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_API_ENDPOINT,
)
print("✅ Azure OpenAI client initialized.")

# =========================
# Ingest documents
# =========================
def sanitize_key(filename):
    """Sanitize filename to valid Azure Search document key.
    Keys can only contain letters, digits, underscore (_), dash (-), or equal sign (=).
    """
    # Remove extension and replace invalid characters with underscores
    key = re.sub(r'[^a-zA-Z0-9_\-=]', '_', filename)
    # Ensure it's not too long (Azure Search has limits)
    return key[:200] if len(key) > 200 else key

def chunk_text(text, max_chunk_size=3000):
    """Split text into chunks to stay within token limits.
    Each chunk should be ~3000 chars to safely stay under 8192 tokens.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_size += len(word) + 1
        current_chunk.append(word)
        
        if current_size >= max_chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_size = 0
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks

def pdf_to_text(pdf_path):
    try:
        reader = PdfReader(str(pdf_path))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
        # Clean up broken words and formatting issues from PDF extraction
        text = re.sub(r'[ \t]+', ' ', text)  # Collapse multiple spaces/tabs
        text = re.sub(r'\n(?=[a-z])', '', text)  # Remove newlines before lowercase (broken words)
        text = re.sub(r'([a-z])\n([a-z])', r'\1\2', text)  # Join words split across lines
        # Fix common broken words with spaces in the middle (e.g., "yo u" -> "you")
        text = re.sub(r'\b([a-z])\s+([a-z]\w*)\b', r'\1\2', text, flags=re.IGNORECASE)
        # Clean up multiple spaces again after fixes
        text = re.sub(r' +', ' ', text)
        # Normalize line breaks (remove excessive newlines)
        text = re.sub(r'\n{2,}', '\n\n', text)
        return text
    except Exception as e:
        print(f"❌ Failed to read {pdf_path.name}: {e}")
        return None

def embed_text(text):
    try:
        response = openai_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"❌ Embedding failed: {e}")
        return None

# Iterate over all PDFs in folder
uploaded_count = 0
for pdf_file in docs_path.glob("*.pdf"):
    print(f"📄 Processing {pdf_file.name}...")
    text = pdf_to_text(pdf_file)
    if not text or len(text.strip()) == 0:
        print(f"⚠️ Skipping {pdf_file.name}: No text extracted.")
        continue

    # Chunk text to stay within token limits (8192 tokens)
    chunks = chunk_text(text)
    sanitized_base_id = sanitize_key(pdf_file.stem)
    
    for chunk_idx, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        if not embedding:
            continue

        # Create unique ID for each chunk: sanitized_filename_chunkN
        chunk_id = f"{sanitized_base_id}_chunk_{chunk_idx}" if len(chunks) > 1 else sanitized_base_id
        
        # Prepare document for Azure Search
        doc = {
            "id": chunk_id,
            "content": chunk,
            "contentVector": embedding
        }

        try:
            search_client.upload_documents(documents=[doc])
            uploaded_count += 1
            if len(chunks) > 1:
                print(f"✅ Uploaded {pdf_file.name} (chunk {chunk_idx + 1}/{len(chunks)})")
            else:
                print(f"✅ Uploaded {pdf_file.name}")
        except Exception as e:
            print(f"❌ Failed to upload {pdf_file.name} (chunk {chunk_idx}): {e}")

if uploaded_count == 0:
    print("⚠️ No documents uploaded.")
else:
    print(f"🎉 Successfully uploaded {uploaded_count} documents.")