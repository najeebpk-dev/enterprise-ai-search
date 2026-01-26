#!/usr/bin/env python
"""
Quick setup script for Enterprise AI Search
Helps verify environment and configuration before running the main application.
"""

import os
import sys
from pathlib import Path


def print_header(text):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def check_python_version():
    """Verify Python version is 3.8 or higher."""
    print("\n🔍 Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print(f"   ✓ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ✗ Python {version.major}.{version.minor}.{version.micro} (need 3.8+)")
        return False


def check_dependencies():
    """Check if required dependencies are installed."""
    print("\n🔍 Checking dependencies...")
    required_packages = [
        "azure.search.documents",
        "azure.core",
        "openai",
        "pypdf",
        "dotenv",
        "tqdm"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✓ {package}")
        except ImportError:
            print(f"   ✗ {package} (missing)")
            missing.append(package)
    
    if missing:
        print("\n⚠️  Install missing packages with:")
        print("   pip install -r requirements.txt")
        return False
    
    return True


def check_env_file():
    """Check if .env file exists and has required variables."""
    print("\n🔍 Checking configuration...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("   ✗ .env file not found")
        print("\n💡 Create .env file:")
        print("   cp .env.example .env")
        print("   Then edit .env with your Azure credentials")
        return False
    
    print("   ✓ .env file exists")
    
    # Try to load and validate
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        required_vars = [
            "SEARCH_ENDPOINT",
            "SEARCH_KEY",
            "INDEX_NAME",
            "OPENAI_ENDPOINT",
            "OPENAI_KEY",
            "EMBEDDING_MODEL",
            "CHAT_MODEL"
        ]
        
        missing = []
        for var in required_vars:
            value = os.getenv(var)
            if not value or value.startswith("your-") or value == "":
                missing.append(var)
                print(f"   ✗ {var} (not configured)")
            else:
                print(f"   ✓ {var}")
        
        if missing:
            print("\n⚠️  Update these variables in your .env file")
            return False
        
        return True
        
    except Exception as e:
        print(f"   ✗ Error loading .env: {e}")
        return False


def check_documents_folder():
    """Check if documents folder exists."""
    print("\n🔍 Checking documents folder...")
    
    docs_path = Path("data/documents")
    if not docs_path.exists():
        print(f"   ✗ {docs_path} not found")
        docs_path.mkdir(parents=True, exist_ok=True)
        print(f"   ✓ Created {docs_path}")
    else:
        print(f"   ✓ {docs_path} exists")
    
    # Check for PDF files
    pdf_files = list(docs_path.glob("*.pdf"))
    if pdf_files:
        print(f"   ✓ Found {len(pdf_files)} PDF file(s)")
    else:
        print("   ⚠️  No PDF files found")
        print("\n💡 Add PDF files to data/documents/ before running ingestion")
    
    return True


def main():
    """Run setup checks."""
    print_header("🚀 ENTERPRISE AI SEARCH - SETUP CHECK")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Configuration", check_env_file),
        ("Documents", check_documents_folder)
    ]
    
    results = []
    for name, check_func in checks:
        try:
            results.append(check_func())
        except Exception as e:
            print(f"\n❌ Error during {name} check: {e}")
            results.append(False)
    
    # Summary
    print_header("📊 SETUP SUMMARY")
    
    if all(results):
        print("\n✅ All checks passed! You're ready to go.")
        print("\n📝 Next steps:")
        print("   1. Run ingestion: python src/ingest.py")
        print("   2. Query the system: python src/query.py")
    else:
        print("\n⚠️  Some checks failed. Please address the issues above.")
        print("\n📚 For help, see README.md")
    
    print()
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
