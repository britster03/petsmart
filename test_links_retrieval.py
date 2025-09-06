import chromadb
from sentence_transformers import SentenceTransformer
import re
import urllib.parse

def test_links_in_rag():
    """Test if RAG is retrieving links from the PetSmart guide"""
    
    # Connect to ChromaDB
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )
    
    collection = client.get_collection("petsmart_documents")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("🔍 Testing link-related queries from PetSmart Guide:\n")
    
    # Test queries that should return pages with links
    link_queries = [
        "partner resource center",
        "grants homepage", 
        "marketing support",
        "partner with us",
        "FAQs frequently asked questions",
        "website links resources",
        "online portal access",
        "URL web address"
    ]
    
    all_found_links = set()
    
    for query in link_queries:
        print(f"Query: '{query}'")
        print("-" * 50)
        
        # Search for documents
        query_embedding = model.encode([query])
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=3,
            include=["documents", "metadatas", "distances"]
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                print(f"  Result {i+1} (similarity: {1-distance:.3f}):")
                print(f"    Source: {metadata.get('document', 'Unknown')} - Page {metadata.get('page', '?')}")
                
                # Look for URLs/links in the document text
                urls = find_urls_in_text(doc)
                if urls:
                    print(f"    🔗 Found {len(urls)} links:")
                    for url in urls:
                        print(f"      • {url}")
                        all_found_links.add(url)
                else:
                    print("    📝 No URLs found in this result")
                
                # Show preview with potential link context
                print(f"    Preview: {doc[:300]}...")
                print()
        
        print("="*60 + "\n")
    
    # Now let's look specifically at PetSmart Guide pages for links
    print("\n🎯 Examining all PetSmart Guide pages for links:")
    print("="*60)
    
    guide_results = collection.get(
        where={"document": "PetSmart Guide"},
        include=["documents", "metadatas"]
    )
    
    if guide_results['documents']:
        for doc, metadata in zip(guide_results['documents'], guide_results['metadatas']):
            page_num = metadata.get('page', '?')
            urls = find_urls_in_text(doc)
            
            if urls:
                print(f"\n📄 Page {page_num} - Found {len(urls)} links:")
                for url in urls:
                    print(f"  🔗 {url}")
                    all_found_links.add(url)
                print(f"  Content preview: {doc[:200]}...")
            else:
                # Look for link-like text even if not proper URLs
                link_indicators = find_link_indicators(doc)
                if link_indicators:
                    print(f"\n📄 Page {page_num} - Found potential link references:")
                    for indicator in link_indicators:
                        print(f"  💡 {indicator}")
                    print(f"  Content preview: {doc[:200]}...")
    
    print(f"\n📊 Summary:")
    print(f"Total unique URLs found: {len(all_found_links)}")
    if all_found_links:
        print("All found links:")
        for link in sorted(all_found_links):
            print(f"  🔗 {link}")
    else:
        print("❌ No direct URLs found in the retrieved content")
        print("💡 This might indicate:")
        print("   - Links were not properly extracted during PDF processing")
        print("   - Links are in a format not recognized by our pattern matching")
        print("   - The guide contains reference text but not clickable URLs")

def find_urls_in_text(text):
    """Find URLs in text using regex patterns"""
    # Common URL patterns
    url_patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',  # http/https URLs
        r'www\.[^\s<>"{}|\\^`\[\]]+',      # www domains
        r'[a-zA-Z0-9][a-zA-Z0-9-]*\.com[^\s<>"{}|\\^`\[\]]*',  # .com domains
        r'[a-zA-Z0-9][a-zA-Z0-9-]*\.org[^\s<>"{}|\\^`\[\]]*',  # .org domains
        r'[a-zA-Z0-9][a-zA-Z0-9-]*\.net[^\s<>"{}|\\^`\[\]]*',  # .net domains
    ]
    
    urls = set()
    for pattern in url_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        urls.update(matches)
    
    return list(urls)

def find_link_indicators(text):
    """Find text that indicates links might be present"""
    indicators = []
    
    # Look for common link-related phrases
    link_phrases = [
        r'visit\s+[^\s]+\.com',
        r'go\s+to\s+[^\s]+\.com',
        r'at\s+[^\s]+\.com',
        r'website[:\s]+[^\s]+',
        r'portal[:\s]+[^\s]+',
        r'link[:\s]+[^\s]+',
        r'homepage[:\s]+[^\s]+',
        r'resource\s+center',
        r'partner\s+portal',
        r'online\s+at',
    ]
    
    for phrase in link_phrases:
        matches = re.findall(phrase, text, re.IGNORECASE)
        indicators.extend(matches)
    
    return indicators

if __name__ == "__main__":
    test_links_in_rag()
