# Enterprise AI Search

[![Python](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/)
[![Azure](https://img.shields.io/badge/azure-cognitive_search-blue)](https://azure.microsoft.com/)
[![Azure OpenAI](https://img.shields.io/badge/azure-openai-purple)](https://learn.microsoft.com/azure/ai-services/openai/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

> Enterprise-grade document search system using **Azure Cognitive Search + Azure OpenAI**  
> Hybrid vector + keyword search for PDF manuals.

---

## 📁 Project Structure
data/ # PDF documents to ingest
src/ # Python modules (search logic + helpers)
ingest.py # Ingest PDFs into Azure Cognitive Search
query.py # CLI-based query interface
.env.example # Environment variable template
.gitignore # Ignore files
requirements.txt # Python dependencies
README.md # Project documentation
