import os
import sys
import re
from pathlib import Path
from dotenv import load_dotenv
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
import openai

# ----------------------------
# Load environment variables
# ----------------------------
dotenv_path = Path(__file__).parent / ".env"
if not dotenv_path.exists():
    print(f"❌ .env file not found at {dotenv_path}")
    sys.exit(1)

load_dotenv(dotenv_path)

# ----------------------------
# Environment variables
# ----------------------------
SEARCH_ENDPOINT = os.getenv("SEARCH_ENDPOINT")
SEARCH_KEY = os.getenv("SEARCH_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "docs-index")
OPENAI_API_ENDPOINT = os.getenv("OPENAI_API_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_VERSION = os.getenv("OPENAI_API_VERSION", "2024-02-01")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")

# Validate critical env vars
missing = []
for var_name, var_val in [
    ("SEARCH_ENDPOINT", SEARCH_ENDPOINT),
    ("SEARCH_KEY", SEARCH_KEY),
    ("INDEX_NAME", INDEX_NAME),
    ("OPENAI_API_ENDPOINT", OPENAI_API_ENDPOINT),
    ("OPENAI_API_KEY", OPENAI_API_KEY),
    ("EMBEDDING_MODEL", EMBEDDING_MODEL),
]:
    if not var_val:
        missing.append(var_name)
if missing:
    print(f"❌ Missing environment variables: {', '.join(missing)}")
    sys.exit(1)

# ----------------------------
# Connect to Azure Cognitive Search
# ----------------------------
search_client = SearchClient(
    endpoint=SEARCH_ENDPOINT,
    index_name=INDEX_NAME,
    credential=AzureKeyCredential(SEARCH_KEY)
)

# ----------------------------
# Initialize Azure OpenAI Client
# ----------------------------
from openai import AzureOpenAI

openai_client = AzureOpenAI(
    api_key=OPENAI_API_KEY,
    api_version=OPENAI_API_VERSION,
    azure_endpoint=OPENAI_API_ENDPOINT,
)

# ----------------------------
# Helper: get embedding
# ----------------------------
def get_embedding(text):
    resp = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=text
    )
    return resp.data[0].embedding

# ----------------------------
# Interactive query loop
# ----------------------------
from azure.search.documents.models import VectorizedQuery

def run_query(query_text):
    """Run a hybrid vector + keyword search for better accuracy."""
    try:
        vector = get_embedding(query_text)
        
        # Create a vectorized query with higher k to get more candidates
        # Then we'll re-rank them based on keyword match quality
        vector_query = VectorizedQuery(vector=vector, k_nearest_neighbors=10, fields="contentVector")
        
        results = list(search_client.search(
            search_text=query_text,  # Keyword search helps with exact matches (e.g., "3820")
            vector_queries=[vector_query],
            top=10  # Get more results to re-rank
        ))
        
        # Re-rank by scoring: boost results that contain exact model numbers from query
        def score_result(result, query_terms):
            score = result.get("@search.score", 0)
            content = result.get("content", "").lower()
            # Boost score if content contains exact model numbers (e.g., "3820", "3712")
            for term in query_terms:
                if term.lower() in content:
                    score += 2.0  # Significant boost for keyword matches
            return score
        
        # Extract model numbers and other key terms from query
        query_terms = query_text.split()
        
        # Sort by re-ranked score
        results.sort(key=lambda r: score_result(r, query_terms), reverse=True)
        
        print("\n--- TOP RESULTS ---")
        result_count = 0
        top_results = []
        for r in results[:3]:  # Show top 3 after re-ranking
            result_count += 1
            top_results.append(r)
            print(f"\n[Result {result_count}] (type '{result_count}' to expand)")
            print(f"ID: {r['id']}")
            print(f"Score: {score_result(r, query_terms):.2f}")
            print(f"Snippet: {r['content'][:300]}...")
        
        if result_count == 0:
            print("No results found.")
            return None
        
        return top_results
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return None

def expand_result(result):
    """Display the full content of a result with better formatting."""
    import textwrap
    
    content = result['content']
    # Clean up any remaining whitespace issues
    content = re.sub(r' +', ' ', content)  # Remove multiple spaces
    content = re.sub(r'\n{3,}', '\n\n', content)  # Remove excessive line breaks
    
    print(f"\n{'='*80}")
    print(f"EXPANDED VIEW - {result['id']}")
    print(f"{'='*80}")
    
    # Wrap text for better readability
    wrapped_lines = []
    for paragraph in content.split('\n'):
        if paragraph.strip():
            wrapped = textwrap.fill(paragraph.strip(), width=80)
            wrapped_lines.append(wrapped)
        else:
            wrapped_lines.append('')
    
    print('\n'.join(wrapped_lines))
    print(f"{'='*80}\n")

def ask_followup(context_text, followup_question):
    """Ask a follow-up question about a specific document chunk."""
    try:
        # Create a context-aware prompt
        full_prompt = f"Based on this information:\n\n{context_text}\n\nAnswer this question: {followup_question}"
        
        # Get embedding for follow-up and search in context
        vector = get_embedding(full_prompt)
        vector_query = VectorizedQuery(vector=vector, k_nearest_neighbors=5, fields="contentVector")
        
        results = list(search_client.search(
            search_text=followup_question,
            vector_queries=[vector_query],
            top=5
        ))
        
        print(f"\n--- FOLLOW-UP RESULTS ---")
        if results:
            for i, r in enumerate(results[:2], 1):
                print(f"\n[Result {i}]")
                print(f"ID: {r['id']}")
                print(f"Snippet: {r['content'][:300]}...")
        else:
            print("No additional results found.")
    except Exception as e:
        print(f"❌ Follow-up search failed: {e}")

print("\n🔍 Vector Search Query Interface")
print("Type 'exit' to quit.\n")

current_results = None
expanded_result = None

while True:
    try:
        if expanded_result:
            prompt = "Enter follow-up question (or 'back' to return to results, 'new' for new search): "
        else:
            prompt = "Enter your question: "
        
        user_input = input(prompt).strip()
        
        if user_input.lower() == 'exit':
            print("Goodbye!")
            break
        elif user_input.lower() == 'back':
            expanded_result = None
            print("Returned to results.")
            continue
        elif user_input.lower() == 'new':
            expanded_result = None
            current_results = None
            continue
        elif not user_input:
            print("Please enter a question or command.")
            continue
        
        # If a result is expanded, treat input as follow-up question
        if expanded_result:
            ask_followup(expanded_result['content'], user_input)
        # If user enters a number 1-3, expand that result
        elif user_input in ['1', '2', '3']:
            result_idx = int(user_input) - 1
            if current_results and result_idx < len(current_results):
                expanded_result = current_results[result_idx]
                expand_result(expanded_result)
            else:
                print("Invalid result number.")
        # Otherwise, run a new search
        else:
            current_results = run_query(user_input)
            expanded_result = None
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        break
    except Exception as e:
        print(f"❌ Error: {e}")