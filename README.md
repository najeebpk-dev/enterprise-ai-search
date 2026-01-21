# Enterprise AI Search

This project demonstrates an **enterprise-grade document search system** built using:

- **Azure Cognitive Search** (vector + keyword hybrid search)
- **Azure OpenAI** (embeddings)
- **PDF ingestion pipeline**
- **CLI-based query interface**

---

## 📁 Project Structure

data/ # PDF documents to ingest
src/ # Python modules
ingest.py # Ingest PDFs into Azure Cognitive Search
query.py # Search interface (CLI)
.env.example # Environment variable template
.gitignore # Ignore files
requirements.txt # Python dependencies
README.md # Project documentation
