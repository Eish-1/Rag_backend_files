# RAG System Technical Documentation

## Overview
This system implements a Retrieval-Augmented Generation (RAG) pipeline that processes PDF documents, creates searchable embeddings, and provides a REST API for querying document content. The system uses FAISS (Facebook AI Similarity Search) for efficient similarity search and Flask for serving API requests.

## System Architecture

### Core Components
1. **PDF Processing Module**
   - Handles extraction of text from PDF documents
   - Splits text into manageable chunks for processing
   - Maintains document metadata and source information

2. **FAISS Document Store**
   - Creates and manages vector embeddings
   - Provides efficient similarity search capabilities
   - Persists embeddings and metadata to disk

3. **REST API Server**
   - Handles incoming query requests
   - Returns relevant document segments
   - Provides similarity scores for results

## Technical Implementation

### Document Processing Pipeline
The system processes documents through several stages:

1. **Text Extraction**
   ```python
   def extract_text_from_pdf(pdf_path):
   ```
   - Opens PDF files in binary mode
   - Extracts text content page by page
   - Concatenates content while preserving structure

2. **Text Chunking**
   ```python
   def split_into_chunks(documents):
   ```
   - Splits documents into smaller segments (default: 500 words)
   - Maintains context with overlapping chunks (default: 50 words)
   - Cleans and preprocesses text

### Vector Store Management
The system uses FAISS for embedding storage and retrieval:

1. **Initialization**
   ```python
   def get_clean_document_store():
   ```
   - Creates or loads FAISS document store
   - Configures embedding dimensions (768-dimensional vectors)
   - Sets up SQLite backend for metadata

2. **Embedding Generation**
   - Uses sentence transformers for creating embeddings
   - Model: "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
   - Processes documents in batches for efficiency

### API Implementation
REST API built with Flask:

1. **Query Endpoint**
   ```python
   @app.route("/query", methods=["POST"])
   ```
   - Accepts POST requests with JSON payload
   - Returns top 3 most relevant document segments
   - Includes similarity scores and source information

## Performance Considerations

### Embedding Persistence
The system implements intelligent embedding management:
- Saves embeddings to disk after creation
- Loads existing embeddings on subsequent runs
- Only recreates embeddings when necessary

### Optimization Features
1. **Batch Processing**
   - Processes documents in batches
   - Optimizes memory usage
   - Improves processing speed

2. **Index Management**
   - Uses "Flat" index type for maximum accuracy
   - Supports persistence of index to disk
   - Enables quick loading of existing indexes

## Usage Guide

### Initial Setup
```bash
# Required directory structure
/your_project_root
  /data           # PDF documents
  /faiss_data    # Generated embeddings
```

### API Usage
```python
# Example query request
POST /query
Content-Type: application/json
{
    "query": "Your search query here"
}

# Example response
{
    "results": [
        {
            "text": "Relevant text segment",
            "source": "source_document.pdf",
            "score": 0.85
        }
    ]
}
```

### Configuration Options
Key parameters that can be modified:
- `CHUNK_SIZE`: Size of text segments (default: 500)
- `CHUNK_OVERLAP`: Overlap between segments (default: 50)
- `EMBEDDING_MODEL`: Model for generating embeddings

## Deployment Considerations

### Production Setup
1. Use a production-grade WSGI server
2. Disable Flask debug mode
3. Implement proper error handling
4. Add authentication if needed

### Performance Optimization
1. Separate initialization and server processes
2. Implement caching for frequent queries
3. Consider batch query processing for high load

## Error Handling
The system implements robust error handling:
- Graceful handling of PDF processing errors
- Recovery from embedding generation failures
- Proper cleanup of resources

## Future Improvements
Potential enhancements:
1. Add support for incremental updates
2. Implement query caching
3. Add document type support beyond PDFs
4. Enhance similarity search algorithms
5. Add authentication and rate limiting

## Maintenance
Regular maintenance tasks:
1. Monitor embedding database size
2. Update sentence transformer models
3. Clean up temporary files
4. Optimize index periodically

