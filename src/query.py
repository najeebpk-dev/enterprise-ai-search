"""
Enterprise AI Search - Query Interface with RAG

This module provides an intelligent search interface that combines:
- Vector similarity search for semantic understanding
- Keyword search for exact matches
- GPT-powered answer generation using retrieved context (RAG pattern)
"""

import logging
from typing import List, Dict, Any
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_config():
    """Validate that all required configuration variables are set."""
    required_vars = {
        'SEARCH_ENDPOINT': SEARCH_ENDPOINT,
        'SEARCH_KEY': SEARCH_KEY,
        'INDEX_NAME': INDEX_NAME,
        'OPENAI_ENDPOINT': OPENAI_ENDPOINT,
        'OPENAI_KEY': OPENAI_KEY,
        'EMBEDDING_MODEL': EMBEDDING_MODEL,
        'CHAT_MODEL': CHAT_MODEL
    }
    
    missing = [name for name, value in required_vars.items() if not value]
    if missing:
        raise ValueError(f"Missing required configuration: {', '.join(missing)}")


class EnterpriseSearchClient:
    """Enterprise search client with RAG capabilities."""
    
    def __init__(self):
        """Initialize Azure Search and OpenAI clients."""
        validate_config()
        
        self.search_client = SearchClient(
            endpoint=SEARCH_ENDPOINT,
            index_name=INDEX_NAME,
            credential=AzureKeyCredential(SEARCH_KEY)
        )
        
        self.openai_client = AzureOpenAI(
            api_key=OPENAI_KEY,
            api_version="2024-02-15-preview",
            azure_endpoint=OPENAI_ENDPOINT
        )
        
        logger.info("✓ Enterprise Search Client initialized")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for query text.
        
        Args:
            text: Query text
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            response = self.openai_client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=[text]
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def hybrid_search(
        self, 
        query: str, 
        top_k: int = 5,
        use_semantic: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining vector and keyword search.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            use_semantic: Whether to use semantic (vector) search
            
        Returns:
            List of search results with content and metadata
        """
        try:
            results = []
            
            if use_semantic:
                # Generate embedding for the query
                query_vector = self.generate_embedding(query)
                
                # Create vector query
                vector_query = VectorizedQuery(
                    vector=query_vector,
                    k_nearest_neighbors=top_k,
                    fields="embedding"
                )
                
                # Hybrid search: vector + keyword
                search_results = self.search_client.search(
                    search_text=query,
                    vector_queries=[vector_query],
                    select=["content", "source_file", "page_number"],
                    top=top_k
                )
            else:
                # Keyword-only search
                search_results = self.search_client.search(
                    search_text=query,
                    select=["content", "source_file", "page_number"],
                    top=top_k
                )
            
            for result in search_results:
                results.append({
                    "content": result["content"],
                    "source_file": result["source_file"],
                    "page_number": result["page_number"],
                    "score": result.get("@search.score", 0)
                })
            
            logger.info(f"Found {len(results)} results for query: '{query}'")
            return results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            raise
    
    def generate_answer(
        self, 
        query: str, 
        context_docs: List[Dict[str, Any]],
        temperature: float = 0.3
    ) -> Dict[str, Any]:
        """
        Generate an answer using GPT with retrieved context (RAG pattern).
        
        Args:
            query: User's question
            context_docs: List of retrieved documents
            temperature: GPT temperature (0-1, lower = more focused)
            
        Returns:
            Dictionary with answer and metadata
        """
        try:
            # Build context from retrieved documents
            context_parts = []
            for i, doc in enumerate(context_docs, 1):
                context_parts.append(
                    f"[Document {i}] Source: {doc['source_file']} (Page {doc['page_number']})\n"
                    f"{doc['content']}\n"
                )
            
            context = "\n".join(context_parts)
            
            # Create prompt for GPT
            system_prompt = """You are an expert assistant helping users find information from enterprise documents.

Your task is to answer the user's question based ONLY on the provided context documents.

Guidelines:
- Provide accurate, concise answers based on the context
- If the context doesn't contain relevant information, say "I don't have enough information to answer that question."
- Cite the source document and page number when possible
- If multiple documents contain relevant information, synthesize them into a coherent answer
- Be professional and clear in your responses"""

            user_prompt = f"""Question: {query}

Context Documents:
{context}

Please provide a clear and accurate answer based on the above context."""

            # Call GPT
            response = self.openai_client.chat.completions.create(
                model=CHAT_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "sources": [
                    {
                        "file": doc["source_file"],
                        "page": doc["page_number"]
                    }
                    for doc in context_docs
                ],
                "model": CHAT_MODEL
            }
            
        except Exception as e:
            logger.error(f"Failed to generate answer: {e}")
            raise
    
    def ask(self, query: str, top_k: int = 5, show_sources: bool = True) -> None:
        """
        Complete RAG pipeline: search + answer generation.
        
        Args:
            query: User's question
            top_k: Number of documents to retrieve
            show_sources: Whether to display source documents
        """
        print("\n" + "=" * 80)
        print(f"🔍 Query: {query}")
        print("=" * 80)
        
        # Step 1: Retrieve relevant documents
        print("\n⏳ Searching knowledge base...")
        results = self.hybrid_search(query, top_k=top_k)
        
        if not results:
            print("\n❌ No relevant documents found.")
            return
        
        print(f"✓ Found {len(results)} relevant documents")
        
        # Step 2: Generate answer using RAG
        print("\n⏳ Generating answer with AI...")
        answer_data = self.generate_answer(query, results)
        
        # Display answer
        print("\n" + "=" * 80)
        print("💡 ANSWER:")
        print("=" * 80)
        print(f"\n{answer_data['answer']}\n")
        
        # Display sources
        if show_sources:
            print("=" * 80)
            print("📚 SOURCES:")
            print("=" * 80)
            for i, source in enumerate(answer_data["sources"], 1):
                print(f"  {i}. {source['file']} (Page {source['page']})")
            
            # Optionally show full context
            show_full = input("\n📄 Show full source documents? (y/n): ").strip().lower()
            if show_full == 'y':
                print("\n" + "=" * 80)
                print("📄 FULL SOURCE DOCUMENTS:")
                print("=" * 80)
                for i, doc in enumerate(results, 1):
                    print(f"\n[{i}] {doc['source_file']} - Page {doc['page_number']} (Score: {doc['score']:.4f})")
                    print("-" * 80)
                    print(doc["content"][:500] + "..." if len(doc["content"]) > 500 else doc["content"])
                    print()
        
        print("=" * 80 + "\n")


def main():
    """Main query interface."""
    print("\n" + "=" * 80)
    print("ENTERPRISE AI SEARCH - INTELLIGENT QUERY INTERFACE")
    print("=" * 80)
    print("\nThis system uses:")
    print("  • Hybrid search (vector + keyword)")
    print("  • RAG (Retrieval-Augmented Generation)")
    print("  • Azure OpenAI GPT for intelligent answers")
    print("\nType 'quit' or 'exit' to end the session.\n")
    print("=" * 80)
    
    try:
        # Initialize search client
        search = EnterpriseSearchClient()
        
        # Interactive query loop
        while True:
            try:
                query = input("\n❓ Ask a question: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                # Process query
                search.ask(query, top_k=5, show_sources=True)
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing query: {e}")
                print(f"\n❌ Error: {e}\n")
    
    except Exception as e:
        logger.error(f"Failed to initialize search client: {e}")
        print(f"\n❌ Initialization failed: {e}")
        print("\nPlease check your configuration in .env file.")


if __name__ == "__main__":
    main()
