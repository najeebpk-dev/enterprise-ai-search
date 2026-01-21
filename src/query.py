from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from openai import AzureOpenAI

from config import (
    SEARCH_ENDPOINT,
    SEARCH_KEY,
    INDEX_NAME,
    OPENAI_ENDPOINT,
    OPENAI_KEY,
    EMBEDDING_MODEL,
    CHAT_MODEL
)

# Initialize clients
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

def embed_query(text: str):
    print("DEBUG EMBEDDING MODEL:", EMBEDDING_MODEL)
    response = openai_client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text]
    )
    return response.data[0].embedding

def main():
    query = input("Ask a question: ")

    vector = embed_query(query)

    results = search_client.search(
        search_text=None,
        vector_queries=[{
            "vector": vector,
            "k": 5,
            "fields": "embedding"
        }],
        select=["content", "source_file", "page_number"]
    )

    print("\n--- ANSWERS ---\n")
    for result in results:
        print(f"Source: {result['source_file']} (page {result['page_number']})")
        print(result["content"])
        print("-" * 50)

if __name__ == "__main__":
    main()
