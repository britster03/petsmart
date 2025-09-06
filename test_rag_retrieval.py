import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np

def test_chromadb_retrieval():
    """Test RAG retrieval from the PetSmart ChromaDB collection"""
    
    # Connect to Chroma Cloud using HttpClient (same as working example)
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )
    
    # Get the collection
    try:
        collection = client.get_collection("petsmart_documents")
        print(f"✅ Connected to collection 'petsmart_documents'")
    except Exception as e:
        print(f"❌ Failed to connect to collection: {e}")
        return
    
    # Check collection stats
    count = collection.count()
    print(f"📊 Collection contains {count} documents")
    
    if count == 0:
        print("⚠️ Collection is empty. Run embeddings.py first to ingest documents.")
        return
    
    # Load the same model used for embeddings
    print("🔄 Loading sentence transformer model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("✅ Model loaded")
    
    # Test queries
    test_queries = [
        "pet training tips",
        "dog grooming services",
        "cat food recommendations",
        "store hours and location",
        "return policy",
    ]
    
    print("\n🔍 Testing RAG retrieval with sample queries:\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"Query {i}: '{query}'")
        print("-" * 50)
        
        try:
            # Encode the query
            query_embedding = model.encode([query])
            
            # Search for similar documents
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=3,  # Top 3 results
                include=["documents", "metadatas", "distances"]
            )
            
            # Display results
            if results['documents'] and len(results['documents'][0]) > 0:
                for j, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                )):
                    print(f"  Result {j+1} (similarity: {1-distance:.3f}):")
                    print(f"    Source: {metadata.get('document', 'Unknown')}")
                    if 'page' in metadata:
                        print(f"    Page: {metadata['page']}")
                    print(f"    Preview: {doc[:200]}...")
                    print()
            else:
                print("  No results found")
                
        except Exception as e:
            print(f"  ❌ Error querying: {e}")
        
        print("\n" + "="*60 + "\n")
    
    # Test peek at collection contents
    print("👀 Sample documents in collection:")
    try:
        sample = collection.peek(limit=3)
        if sample['documents']:
            for i, (doc, metadata) in enumerate(zip(sample['documents'], sample['metadatas'])):
                print(f"  Sample {i+1}:")
                print(f"    Source: {metadata.get('document', 'Unknown')}")
                if 'page' in metadata:
                    print(f"    Page: {metadata['page']}")
                print(f"    Preview: {doc[:150]}...")
                print()
    except Exception as e:
        print(f"  ❌ Error peeking at collection: {e}")

def test_query_with_filters():
    """Test querying with metadata filters"""
    print("\n🎯 Testing filtered queries:")
    
    # Connect to collection
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )
    
    collection = client.get_collection("petsmart_documents")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    query = "pet care"
    query_embedding = model.encode([query])
    
    # Test different filters
    filters = [
        {"document": "PetSmart Guide"},
        {"document": "PetSmart Manual"},
    ]
    
    for filter_condition in filters:
        print(f"\nFiltering by: {filter_condition}")
        try:
            results = collection.query(
                query_embeddings=query_embedding.tolist(),
                n_results=2,
                where=filter_condition,
                include=["documents", "metadatas", "distances"]
            )
            
            if results['documents'] and len(results['documents'][0]) > 0:
                for doc, metadata, distance in zip(
                    results['documents'][0], 
                    results['metadatas'][0], 
                    results['distances'][0]
                ):
                    print(f"  Page {metadata.get('page', '?')}: {doc[:100]}...")
            else:
                print("  No results found with this filter")
                
        except Exception as e:
            print(f"  ❌ Error with filter: {e}")

if __name__ == "__main__":
    print("🚀 Starting ChromaDB RAG Retrieval Test")
    print("="*50)
    
    test_chromadb_retrieval()
    test_query_with_filters()
    
    print("\n✅ RAG retrieval test completed!")
