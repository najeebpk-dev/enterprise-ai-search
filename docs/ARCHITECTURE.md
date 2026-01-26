# Architecture Documentation

## System Overview

Enterprise AI Search is a Retrieval-Augmented Generation (RAG) system that combines semantic search with large language models to provide intelligent answers from document collections.

## Components

### 1. Document Ingestion Pipeline (`src/ingest.py`)

**Purpose**: Extract, embed, and index documents

**Flow**:
```
PDF Documents → Text Extraction → Embedding Generation → Index Upload
```

**Key Features**:
- Page-level chunking for precise citations
- Batch processing for efficiency (50 docs/batch)
- Comprehensive error handling
- Progress tracking with tqdm

**Azure Resources Used**:
- Azure OpenAI (text-embedding-3-small)
- Azure Cognitive Search (index management)

### 2. Query Interface (`src/query.py`)

**Purpose**: Search and answer user questions

**Flow**:
```
User Query → Query Embedding → Hybrid Search → Context Retrieval → GPT Answer Generation → Display
```

**Search Strategy**:
- **Vector Search**: Semantic similarity using embeddings
- **Keyword Search**: BM25-based text matching
- **Hybrid**: Combines both for optimal results

**RAG Implementation**:
1. Retrieve top-k relevant documents (default: 5)
2. Build context from retrieved content
3. Generate answer using GPT-4o-mini (or your chat deployment) with context
4. Provide source attribution

### 3. Configuration (`src/config.py`)

**Purpose**: Centralized configuration management

**Features**:
- Environment variable loading
- Configuration validation
- Easy customization

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                     INGESTION PHASE                     │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌──────────────┐
                    │  PDF Files   │
                    └──────┬───────┘
                           │
                           ▼
                  ┌────────────────┐
                  │ Text Extraction│ (pypdf)
                  └────────┬───────┘
                           │
                           ▼
                ┌──────────────────────┐
                │ Generate Embeddings  │ (Azure OpenAI)
                │   text-embedding-    │
                │     3-small          │
                └──────────┬───────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │  Upload to Search Index    │
              │  - Content (text)          │
              │  - Embedding (vector)      │
              │  - Metadata (source, page) │
              └────────────┬───────────────┘
                           │
                           ▼
              ┌────────────────────────────┐
              │  Azure Cognitive Search    │
              │  - Vector Index (HNSW)     │
              │  - Keyword Index (BM25)    │
              └────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│                      QUERY PHASE                        │
└─────────────────────────────────────────────────────────┘
                            │
                            ▼
                   ┌─────────────────┐
                   │  User Question  │
                   └────────┬────────┘
                            │
                            ▼
                ┌───────────────────────┐
                │ Generate Query Vector │ (Azure OpenAI)
                └───────────┬───────────┘
                            │
                            ▼
            ┌───────────────────────────────┐
            │      Hybrid Search            │
            │  - Vector Similarity (cosine) │
            │  - Keyword Match (BM25)       │
            └───────────┬───────────────────┘
                        │
                        ▼
          ┌─────────────────────────────┐
          │  Retrieve Top-K Documents   │
          │  (with scores & metadata)   │
          └─────────────┬───────────────┘
                        │
                        ▼
            ┌───────────────────────────┐
            │  Build Context from Docs  │
            └───────────┬───────────────┘
                        │
                        ▼
          ┌─────────────────────────────────┐
            │  GPT-4o-mini Answer Generation (RAG)  │
          │  - System: Expert assistant     │
          │  - Context: Retrieved docs      │
          │  - Query: User question         │
          └─────────────┬───────────────────┘
                        │
                        ▼
            ┌───────────────────────────┐
            │  Display Answer + Sources │
            └───────────────────────────┘
```

## Vector Search Details

### HNSW Algorithm

**Hierarchical Navigable Small World (HNSW)** is used for approximate nearest neighbor search.

**Parameters**:
- `m=4`: Connections per layer (higher = better recall, more memory)
- `efConstruction=400`: Candidates during build (higher = better index quality)
- `efSearch=500`: Candidates during search (higher = better recall, slower)
- `metric=cosine`: Cosine similarity for distance

**Trade-offs**:
- **Recall vs Speed**: Higher parameters = better results, slower queries
- **Memory vs Accuracy**: More connections = more memory, better paths

### Embedding Model

**text-embedding-3-small**:
- Dimension: 1536
- Max tokens: ~8,191
- Use case: General-purpose semantic understanding
- Cost-effective and performant

## RAG Pattern Implementation

### Retrieval Strategy

1. **Query Understanding**: Convert natural language to embedding
2. **Hybrid Matching**: Combine semantic + keyword signals
3. **Ranking**: Score-based result ordering
4. **Context Selection**: Top-k most relevant chunks

### Generation Strategy

1. **Context Assembly**: Concatenate retrieved documents
2. **Prompt Engineering**: 
   - System role: Expert assistant
   - Instructions: Use context only, cite sources
   - Context: Retrieved documents with metadata
   - Query: User question
3. **Temperature Control**: 0.3 (focused) to 0.7 (creative)
4. **Token Management**: Max 500 tokens for answer

### Source Attribution

- Each retrieved document includes source file and page number
- GPT answer references specific sources
- User can view full context on demand

## Scalability Considerations

### Current Implementation

- **Documents**: Suitable for 1K-100K documents
- **Index Size**: ~20 GB limit per partition (Azure Search)
- **Query Latency**: <1 second for search, 2-5s for answer generation

### Scaling Strategies

1. **Horizontal Scaling**:
   - Use Azure Search partitions for larger datasets
   - Implement sharding for multi-index scenarios

2. **Vertical Scaling**:
   - Increase Azure Search tier for more capacity
   - Use GPT-4o-mini for lower latency; upgrade to GPT-4o for higher quality

3. **Optimization**:
   - Cache common queries
   - Pre-compute embeddings for static content
   - Implement query routing for specialized indexes

## Security Architecture

### Authentication & Authorization

- API keys stored in environment variables (dev)
- Azure Key Vault recommended for production
- Managed Identity for Azure resource access

### Data Protection

- TLS 1.2+ for all API calls
- Data encrypted at rest (Azure default)
- No credential logging

### Access Control

- Azure RBAC for resource management
- IP restrictions for production endpoints
- Private Link for network isolation

## Monitoring & Observability

### Logging

- Structured logging with Python logging module
- INFO: Operational events
- ERROR: Failures and exceptions
- DEBUG: Detailed diagnostic information

### Metrics

Track:
- Documents ingested per run
- Query latency (search + generation)
- Error rates
- API usage and costs

### Azure Integration

- Application Insights for telemetry
- Azure Monitor for resource metrics
- Log Analytics for centralized logging

## Cost Optimization

### Ingestion Costs

- **Embedding API**: ~$0.0001 per 1K tokens
- **Search Indexing**: Free for Basic tier, paid for Standard+

### Query Costs

- **Embedding API**: ~$0.0001 per query
- **GPT-4o-mini API**: see current Azure OpenAI pricing (typically lower than GPT-4o)
- **Search Queries**: Depends on tier (free tier: 3/sec)

### Optimization Tips

1. Cache embeddings during ingestion
2. Use GPT-3.5-Turbo for cost-sensitive scenarios
3. Implement query caching for common questions
4. Batch document processing
5. Use Azure Search free tier for development

## Future Architecture Enhancements

1. **Multi-Modal Support**: Images, tables, charts
2. **Real-Time Updates**: Incremental indexing
3. **Advanced RAG**: Re-ranking, query expansion
4. **User Feedback Loop**: Continuous improvement
5. **Distributed Processing**: Apache Spark for large-scale ingestion
