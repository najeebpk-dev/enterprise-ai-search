# 🔍 Enterprise AI Search

> An intelligent document search system with **RAG (Retrieval-Augmented Generation)** capabilities, built on Azure Cognitive Search and Azure OpenAI.

This portfolio project demonstrates production-ready AI search architecture, combining vector embeddings, hybrid search, and GPT-powered answer generation to deliver enterprise-grade document intelligence.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Azure](https://img.shields.io/badge/Azure-Cognitive_Search-0078D4.svg)](https://azure.microsoft.com/services/search/)
[![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4-74aa9c.svg)](https://azure.microsoft.com/products/ai-services/openai-service)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

---

## ✨ Features

### 🎯 Core Capabilities
- **📄 PDF Document Ingestion** - Automated pipeline for extracting and indexing PDF documents
- **🧠 Vector Embeddings** - Semantic understanding using Azure OpenAI embeddings (text-embedding-3-small or your deployed embedding model)
- **🔎 Hybrid Search** - Combines vector similarity and keyword search for optimal results
- **💬 RAG-Powered Answers** - Intelligent answer generation using GPT-4o-mini (or your chat model deployment) with retrieved context
- **📊 Source Attribution** - Clear citations linking answers back to source documents

### ⚙️ Technical Features
- **Batch Processing** - Efficient document upload with configurable batch sizes
- **HNSW Algorithm** - High-performance vector search using Hierarchical Navigable Small World graphs
- **Progress Tracking** - Real-time progress bars and detailed logging
- **Error Handling** - Comprehensive validation and graceful error recovery
- **Configuration Management** - Environment-based configuration with validation

---

## 📁 Project Structure

```
enterprise-ai-search/
├── data/
│   └── documents/          # Place your PDF files here
├── src/
│   ├── config.py          # Configuration management
│   ├── ingest.py          # Document ingestion pipeline
│   ├── query.py           # Search and RAG interface
│   └── test_embedding.py  # Embedding validation tool
├── .env.example           # Environment variable template
├── .gitignore            # Git ignore rules
├── requirements.txt       # Python dependencies
├── LICENSE               # MIT License
└── README.md             # This file
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Azure subscription with:
  - [Azure Cognitive Search](https://azure.microsoft.com/services/search/) instance
  - [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service) resource with:
    - `text-embedding-3-small` deployment (or your chosen embedding model name)
    - `gpt-4o-mini` deployment (or your chosen chat model name)

### 1. Clone and Setup

```bash
# Clone the repository (replace with your GitHub username)
git clone https://github.com/najeebpk-dev/enterprise-ai-search.git
cd enterprise-ai-search

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your Azure credentials
# Use your favorite text editor (VS Code, notepad, etc.)
```

**Required Configuration (.env):**
```env
# Azure Cognitive Search
SEARCH_ENDPOINT=https://your-search-service.search.windows.net
SEARCH_KEY=your-search-admin-key
INDEX_NAME=docs-index

# Azure OpenAI
OPENAI_ENDPOINT=https://your-openai-resource.openai.azure.com/
OPENAI_KEY=your-openai-api-key
EMBEDDING_MODEL=text-embedding-3-small   # use your embedding deployment name
CHAT_MODEL=gpt-4o-mini                   # use your chat deployment name
```

### 3. Add Documents

```bash
# Place your PDF files in the data/documents folder
cp your-documents/*.pdf data/documents/
```

### 4. Ingest Documents

```bash
# Run the ingestion pipeline
python src/ingest.py
```

**Example Output:**
```
============================================================
ENTERPRISE AI SEARCH - DOCUMENT INGESTION PIPELINE
============================================================
✓ Configuration validated successfully
✓ Azure clients initialized
✓ Index 'docs-index' created/updated successfully with vector search

Processing PDFs: 100%|████████████| 10/10 [00:45<00:00,  4.5s/file]

============================================================
INGESTION COMPLETE
============================================================
Files processed: 10
Pages uploaded: 127
Errors: 0
============================================================
```

### 5. Query the System

```bash
# Launch the interactive query interface
python src/query.py
```

**Example Session:**
```
============================================================
ENTERPRISE AI SEARCH - INTELLIGENT QUERY INTERFACE
============================================================

❓ Ask a question: How do I configure the network settings?

⏳ Searching knowledge base...
✓ Found 5 relevant documents

⏳ Generating answer with AI...

============================================================
💡 ANSWER:
============================================================

To configure network settings, follow these steps:
1. Access the network configuration menu from the device settings
2. Select your network type (Ethernet or Wi-Fi)
3. Enter the IP address or enable DHCP...

============================================================
📚 SOURCES:
============================================================
  1. Cisco IP Phone 8841 Manual.pdf (Page 42)
  2. Dell Latitude 3120 Manual.pdf (Page 156)
============================================================
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│   PDF Files     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│   Ingestion Pipeline        │
│   (src/ingest.py)          │
│                             │
│  • Extract text from PDFs   │
│  • Generate embeddings      │
│  • Upload to Azure Search   │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  Azure Cognitive Search     │
│                             │
│  • Vector index (HNSW)      │
│  • Keyword index            │
│  • Hybrid search            │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│   Query Interface           │
│   (src/query.py)           │
│                             │
│  1. User asks question      │
│  2. Generate query vector   │
│  3. Hybrid search           │
│  4. Retrieve top-k docs     │
│  5. GPT generates answer    │
│  6. Display with sources    │
└─────────────────────────────┘
```

### How It Works

1. **Document Ingestion** ([src/ingest.py](src/ingest.py))
   - Extracts text from PDF files page by page
   - Generates 1536-dimensional embeddings using Azure OpenAI
   - Creates search index with vector and text fields
   - Uploads documents in batches for efficiency

2. **Query Processing** ([src/query.py](src/query.py))
   - Converts user query to embedding vector
   - Performs hybrid search (vector + keyword)
   - Retrieves top-k most relevant document chunks
  - Uses GPT-4o-mini to generate contextual answer (RAG)
   - Provides source attribution for transparency

---

## 🛠️ Technology Stack

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Search Engine** | Azure Cognitive Search | Vector + keyword indexing and retrieval |
| **Embeddings** | Azure OpenAI (text-embedding-3-small) | Semantic text understanding |
| **LLM** | Azure OpenAI (GPT-4o-mini) | Answer generation (RAG) |
| **Vector Algorithm** | HNSW | Fast approximate nearest neighbor search |
| **PDF Processing** | pypdf | Text extraction from documents |
| **Language** | Python 3.8+ | Core implementation |
| **Config** | python-dotenv | Environment management |

---

## 📊 Performance Considerations

### Vector Search Configuration
- **Algorithm**: HNSW (Hierarchical Navigable Small World)
- **Parameters**:
  - `m=4`: Number of bi-directional links per node
  - `efConstruction=400`: Size of dynamic candidate list during index construction
  - `efSearch=500`: Size of dynamic candidate list during search
  - `metric=cosine`: Distance metric for similarity

### Optimization Tips
1. **Embedding Dimension**: 1536 (text-embedding-3-small standard)
2. **Batch Size**: Default 50 documents per upload
3. **Top-K Results**: Default 5 for optimal RAG context
4. **Text Chunking**: Page-level granularity for accurate citations

---

## 🔧 Advanced Usage

### Custom Search Parameters

```python
from src.query import EnterpriseSearchClient

search = EnterpriseSearchClient()

# Retrieve more documents for complex queries
results = search.hybrid_search(query="complex question", top_k=10)

# Keyword-only search (faster, no embeddings)
results = search.hybrid_search(query="exact phrase", use_semantic=False)

# Adjust GPT temperature for creativity
answer = search.generate_answer(
    query="question",
    context_docs=results,
    temperature=0.7  # Higher = more creative
)
```

### Testing Embeddings

```bash
# Verify your embedding configuration
python src/test_embedding.py
```

---

## 🐛 Troubleshooting

### Common Issues

**1. "Missing required configuration" Error**
```bash
# Verify your .env file has all required variables
cat .env

# Check that values are not empty or contain placeholder text
```

**2. "Failed to generate embedding" Error**
```bash
# Verify your Azure OpenAI deployment name matches EMBEDDING_MODEL
# Check that your API key has access to the deployment
```

**3. "No results found" After Ingestion**
```bash
# Ensure documents were uploaded successfully
# Check ingestion logs for errors
# Verify INDEX_NAME matches between ingest.py and query.py
```

**4. Rate Limiting (HTTP 429)**
```bash
# Azure OpenAI has rate limits
# Solution: Reduce batch size in ingest.py
# Or: Wait and retry failed documents
```

---

## 📈 Future Enhancements

- [ ] Web interface with Streamlit or Gradio
- [ ] Support for additional file formats (DOCX, TXT, HTML)
- [ ] Multi-tenant support with access controls
- [ ] Advanced chunking strategies (semantic, overlap)
- [ ] Query history and analytics
- [ ] Feedback loop for answer quality
- [ ] Docker containerization
- [ ] CI/CD pipeline with GitHub Actions
- [ ] Unit and integration tests

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with [Azure Cognitive Search](https://azure.microsoft.com/services/search/)
- Powered by [Azure OpenAI](https://azure.microsoft.com/products/ai-services/openai-service)
- Inspired by modern RAG architectures and enterprise search best practices

---

## 📞 Contact

For questions, feedback, or collaboration opportunities:

- **GitHub Issues**: [Open an issue](../../issues)
- **LinkedIn**: [Connect with me on LinkedIn](https://linkedin.com/in/yourprofile)
- **Email**: Contact via GitHub profile

Project Link: [https://github.com/najeebpk-dev/enterprise-ai-search](https://github.com/najeebpk-dev/enterprise-ai-search)

---

<div align="center">
  <sub>Built with ❤️ for intelligent document search</sub>
</div>

