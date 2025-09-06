import chromadb
from sentence_transformers import SentenceTransformer
import json
import re

def test_enhanced_rag_with_links():
    """Test the enhanced RAG system that now includes hyperlinks"""
    
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )
    
    collection = client.get_collection("petsmart_documents")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    
    print("🚀 Testing Enhanced RAG with Hyperlinks")
    print("="*60)
    
    # Test link-related queries
    queries = [
        "partner resource center",
        "grant application",
        "marketing support logos",
        "adoption partner manual", 
        "social media accounts",
        "contact email addresses",
        "brand guidelines",
        "event grants"
    ]
    
    all_found_links = set()
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 50)
        
        query_embedding = model.encode([query])
        results = collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=2,
            include=["documents", "metadatas", "distances"]
        )
        
        if results['documents'] and len(results['documents'][0]) > 0:
            for i, (doc, metadata, distance) in enumerate(zip(
                results['documents'][0], 
                results['metadatas'][0], 
                results['distances'][0]
            )):
                print(f"  📄 Result {i+1} (similarity: {1-distance:.3f}):")
                print(f"     Source: {metadata.get('document')} - Page {metadata.get('page')}")
                print(f"     Links found: {metadata.get('links_count', 0)}")
                
                # Parse and display the links
                links_json = metadata.get('links_json', '[]')
                try:
                    links = json.loads(links_json)
                    if links:
                        print(f"     🔗 Hyperlinks on this page:")
                        for link in links:
                            link_text = link.get('text', 'No text')
                            link_url = link.get('url', 'No URL')
                            print(f"       • {link_text} → {link_url}")
                            all_found_links.add(link_url)
                    else:
                        print(f"     📝 No hyperlinks on this page")
                except:
                    print(f"     ⚠️ Error parsing links")
                
                # Show how URLs are embedded in the text
                embedded_urls = re.findall(r'\[([^\]]+)\]', doc)
                if embedded_urls:
                    print(f"     📎 URLs embedded in text: {len(embedded_urls)} found")
                    for url in embedded_urls[:3]:  # Show first 3
                        print(f"       → {url}")
                
                print(f"     Preview: {doc[:200]}...")
                print()
        
    # Summary of all found links
    print(f"\n📊 SUMMARY:")
    print(f"Total unique URLs discovered: {len(all_found_links)}")
    print(f"\n🔗 All discovered hyperlinks:")
    
    # Categorize links
    categories = {
        'Resource Centers': [],
        'Grant Applications': [],
        'Marketing/Branding': [],
        'Social Media': [],
        'Contact/Email': [],
        'Partner Tools': [],
        'Other': []
    }
    
    for url in sorted(all_found_links):
        if 'resources' in url:
            categories['Resource Centers'].append(url)
        elif 'grant' in url or 'apply' in url:
            categories['Grant Applications'].append(url)
        elif 'marketing' in url or 'logo' in url or 'brand' in url:
            categories['Marketing/Branding'].append(url)
        elif any(social in url for social in ['facebook', 'instagram', 'twitter', 'youtube']):
            categories['Social Media'].append(url)
        elif 'mailto:' in url:
            categories['Contact/Email'].append(url)
        elif 'partner' in url or 'lookup' in url or 'manual' in url:
            categories['Partner Tools'].append(url)
        else:
            categories['Other'].append(url)
    
    for category, urls in categories.items():
        if urls:
            print(f"\n  📁 {category}:")
            for url in urls:
                print(f"    • {url}")

def test_specific_guide_pages():
    """Test retrieval from specific PetSmart Guide pages with many links"""
    
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )
    
    collection = client.get_collection("petsmart_documents")
    
    print(f"\n🎯 Examining PetSmart Guide pages directly:")
    print("="*60)
    
    guide_pages = collection.get(
        where={"document": "PetSmart Guide"},
        include=["documents", "metadatas"]
    )
    
    total_links = 0
    
    for doc, metadata in zip(guide_pages['documents'], guide_pages['metadatas']):
        page_num = metadata.get('page')
        links_count = metadata.get('links_count', 0)
        total_links += links_count
        
        print(f"\n📄 Page {page_num} - {links_count} hyperlinks")
        
        if links_count > 0:
            links_json = metadata.get('links_json', '[]')
            try:
                links = json.loads(links_json)
                for i, link in enumerate(links, 1):
                    print(f"  {i:2d}. {link.get('text', 'No text')}")
                    print(f"      → {link.get('url', 'No URL')}")
            except:
                print("     ⚠️ Error parsing links")
        
        # Show a preview of the enhanced text
        preview = doc[:300].replace('\n', ' ')
        print(f"  Text preview: {preview}...")
    
    print(f"\n📊 Total hyperlinks in PetSmart Guide: {total_links}")

if __name__ == "__main__":
    test_enhanced_rag_with_links()
    test_specific_guide_pages()
