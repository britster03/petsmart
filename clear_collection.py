import chromadb

def clear_collection():
    """Clear the existing collection to re-ingest with hyperlinks"""
    
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )
    
    try:
        # Delete the existing collection
        client.delete_collection("petsmart_documents")
        print("✅ Deleted existing 'petsmart_documents' collection")
    except Exception as e:
        print(f"⚠️ Collection may not exist: {e}")
    
    # Create a fresh collection
    try:
        collection = client.create_collection("petsmart_documents")
        print("✅ Created fresh 'petsmart_documents' collection")
        
        count = collection.count()
        print(f"📊 Collection now has {count} documents (should be 0)")
        
    except Exception as e:
        print(f"❌ Error creating collection: {e}")

if __name__ == "__main__":
    print("🧹 Clearing ChromaDB collection for fresh ingestion with hyperlinks")
    clear_collection()
    print("✅ Ready for re-ingestion with enhanced link extraction!")
