"""
Alternative API Response Format Adapters

This module shows how to adapt different Langflow API response formats
to work with our PetSmart RAG Assistant interface.
"""

def adapt_simple_response(response):
    """
    Adapt a simple response format to our expected structure.
    
    Input format:
    {
        "result": "answer text",
        "sources": ["source1", "source2"]
    }
    """
    return {
        "answer": response.get("result", "No answer provided"),
        "chunks": [
            {
                "text": source,
                "metadata": {
                    "document": "Unknown",
                    "page": i + 1,
                    "snippet": source[:50],
                    "pdf_path": "unknown.pdf",
                    "links_count": 0,
                    "links_json": "[]"
                },
                "similarity": 0.5  # Default similarity
            }
            for i, source in enumerate(response.get("sources", []))
        ]
    }

def adapt_openai_response(response):
    """
    Adapt OpenAI-style response to our format.
    
    Input format:
    {
        "choices": [
            {
                "message": {
                    "content": "answer text"
                }
            }
        ],
        "usage": {...}
    }
    """
    content = ""
    if response.get("choices") and len(response["choices"]) > 0:
        content = response["choices"][0].get("message", {}).get("content", "")
    
    return {
        "answer": content,
        "chunks": []  # No source chunks in this format
    }

def adapt_langchain_response(response):
    """
    Adapt LangChain RetrievalQA response to our format.
    
    Input format:
    {
        "result": "answer text",
        "source_documents": [
            {
                "page_content": "document text",
                "metadata": {
                    "source": "path/to/file.pdf",
                    "page": 1
                }
            }
        ]
    }
    """
    chunks = []
    for doc in response.get("source_documents", []):
        chunks.append({
            "text": doc.get("page_content", ""),
            "metadata": {
                "document": doc.get("metadata", {}).get("source", "Unknown"),
                "page": doc.get("metadata", {}).get("page", 1),
                "snippet": doc.get("page_content", "")[:50],
                "pdf_path": doc.get("metadata", {}).get("source", "unknown.pdf"),
                "links_count": 0,
                "links_json": "[]"
            },
            "similarity": 0.8  # Default high similarity for retrieved docs
        })
    
    return {
        "answer": response.get("result", "No answer provided"),
        "chunks": chunks
    }

def adapt_custom_rag_response(response):
    """
    Adapt a custom RAG response format.
    
    Input format:
    {
        "answer": "text",
        "context": [
            {
                "content": "text",
                "source": "file.pdf",
                "page_number": 1,
                "relevance_score": 0.95
            }
        ]
    }
    """
    chunks = []
    for ctx in response.get("context", []):
        chunks.append({
            "text": ctx.get("content", ""),
            "metadata": {
                "document": ctx.get("source", "Unknown"),
                "page": ctx.get("page_number", 1),
                "snippet": ctx.get("content", "")[:50],
                "pdf_path": ctx.get("source", "unknown.pdf"),
                "links_count": 0,
                "links_json": "[]"
            },
            "similarity": ctx.get("relevance_score", 0.5)
        })
    
    return {
        "answer": response.get("answer", "No answer provided"),
        "chunks": chunks
    }

# Example usage in your Streamlit app:
"""
# In your call_langflow_api method, after getting the response:

def call_langflow_api(self, query: str) -> Dict[str, Any]:
    # ... make API call ...
    raw_response = response.json()
    
    # Detect response format and adapt
    if "result" in raw_response and "sources" in raw_response:
        return adapt_simple_response(raw_response)
    elif "choices" in raw_response:
        return adapt_openai_response(raw_response)
    elif "source_documents" in raw_response:
        return adapt_langchain_response(raw_response)
    elif "context" in raw_response:
        return adapt_custom_rag_response(raw_response)
    else:
        # Assume it's already in our expected format
        return raw_response
"""

# Validation function
def validate_response_format(response):
    """
    Validate that a response matches our expected format.
    Returns (is_valid, error_message)
    """
    if not isinstance(response, dict):
        return False, "Response must be a dictionary"
    
    if "answer" not in response:
        return False, "Missing required 'answer' field"
    
    if "chunks" not in response:
        return False, "Missing required 'chunks' field"
    
    if not isinstance(response["chunks"], list):
        return False, "'chunks' must be an array"
    
    for i, chunk in enumerate(response["chunks"]):
        if not isinstance(chunk, dict):
            return False, f"Chunk {i} must be a dictionary"
        
        if "text" not in chunk:
            return False, f"Chunk {i} missing required 'text' field"
        
        if "similarity" not in chunk:
            return False, f"Chunk {i} missing required 'similarity' field"
        
        if not isinstance(chunk["similarity"], (int, float)):
            return False, f"Chunk {i} 'similarity' must be a number"
    
    return True, "Valid format"
