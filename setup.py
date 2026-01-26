"""
Setup script for Enterprise AI Search
"""
from pathlib import Path
from setuptools import setup, find_packages

# Read the README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="enterprise-ai-search",
    version="1.0.0",
    author="Enterprise AI Search Contributors",
    author_email="contact@example.com",
    description="Enterprise-grade document search with RAG capabilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/najeebpk-dev/enterprise-ai-search",  # Update with your GitHub username
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "azure-search-documents>=11.6.0",
        "azure-core>=1.38.0",
        "openai>=1.7.0",
        "pypdf>=4.0.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
    ],
    entry_points={
        "console_scripts": [
            "enterprise-search-ingest=src.ingest:main",
            "enterprise-search-query=src.query:main",
        ],
    },
)
