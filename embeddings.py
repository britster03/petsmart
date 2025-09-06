import chromadb
import fitz  # PyMuPDF
from sentence_transformers import SentenceTransformer
import os
import json

def ingest_petsmart_pdfs(pdf_files, collection_name):
    """Ingest PetSmart PDFs using the proven pattern from ingest_books"""
    # 1) Connect to Chroma Cloud using HttpClient (like the working example)
    client = chromadb.HttpClient(
        ssl=True,
        host="api.trychroma.com", 
        tenant="986f4b43-03a2-4f26-a81f-311f83dff543",
        database="petsmart",
        headers={"x-chroma-token": "ck-CDL5JjQRp9qevD2XvUgaUtsMPGE6J2WRmgMsbEJdsLvj"}
    )

    # 2) Get or create the collection
    try:
        collection = client.get_collection(collection_name)
        print(f"[ingest_petsmart_pdfs] Using existing collection '{collection_name}'.")
    except Exception:
        collection = client.create_collection(name=collection_name)
        print(f"[ingest_petsmart_pdfs] Created new collection '{collection_name}'.")

    # 3) Quick skip if *any* embeddings are already there
    total = collection.count()
    if total > 0:
        print(f"[ingest_petsmart_pdfs] Collection already has {total} embeddings; skipping full ingestion.")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        return client, collection, model

    # 4) Load embedder
    model = SentenceTransformer("all-MiniLM-L6-v2")
    MAX_BATCH = 100

    # 5) Ingest each PDF, page by page (following the working pattern)
    for pidx, pdf_info in enumerate(pdf_files):
        pdf_path = pdf_info["path"]
        title = pdf_info["title"]

        if not os.path.exists(pdf_path):
            print(f"[ingest_petsmart_pdfs] File not found, skipping: {pdf_path}")
            continue

        doc = fitz.open(pdf_path)

        # Check which pages of *this* PDF are already in
        try:
            small = collection.get(
                where={"pdf_path": pdf_path},
                include=["metadatas"]
            )
            done = {md["page"] for md in small.get("metadatas", [])}
        except Exception:
            done = set()

        to_do = [p+1 for p in range(doc.page_count) if (p+1) not in done]
        if not to_do:
            print(f"[ingest_petsmart_pdfs] All {doc.page_count} pages of '{title}' are already ingested.")
            continue

        print(f"[ingest_petsmart_pdfs] Ingesting {len(to_do)}/{doc.page_count} pages of '{title}'")

        texts, metas, ids = [], [], []
        for page_num in to_do:
            page = doc.load_page(page_num-1)
            
            # Get original text
            text = page.get_text("text") or ""
            
            # Extract hyperlinks and create enhanced text
            links = page.get_links()
            enhanced_text = text
            extracted_links = []
            
            for link in links:
                if 'from' in link and 'uri' in link:
                    try:
                        rect = fitz.Rect(link['from'])
                        link_text = page.get_textbox(rect).strip()
                        uri = link['uri']
                        
                        if link_text and uri:
                            # Create enhanced text with embedded URLs
                            enhanced_link = f"{link_text} [{uri}]"
                            enhanced_text = enhanced_text.replace(link_text, enhanced_link, 1)
                            extracted_links.append({
                                'text': link_text,
                                'url': uri
                            })
                    except:
                        # Skip problematic links
                        continue
            
            # Use enhanced text that includes URLs
            texts.append(enhanced_text)
            metas.append({
                "page": page_num,
                "document": title,
                "snippet": enhanced_text[:50],
                "pdf_path": pdf_path,
                "links_count": len(extracted_links),
                "links_json": json.dumps(extracted_links)  # Store as JSON string
            })
            ids.append(f"p{pidx}_page{page_num}")

        # Encode & push in batches
        emb = model.encode(texts)
        for i in range(0, len(ids), MAX_BATCH):
            batch_ids = ids[i:i+MAX_BATCH]
            batch_docs = texts[i:i+MAX_BATCH]
            batch_mets = metas[i:i+MAX_BATCH]
            batch_embs = emb[i:i+MAX_BATCH].tolist()
            collection.add(
                ids=batch_ids,
                documents=batch_docs,
                metadatas=batch_mets,
                embeddings=batch_embs
            )

        print(f"[ingest_petsmart_pdfs] Finished '{title}'")
        doc.close()

    return client, collection, model

if __name__ == "__main__":
    # Define the PDF files in the same format as the working example
    pdf_files = [
        {
            "path": "petsmart_guide.pdf",
            "title": "PetSmart Guide"
        },
        {
            "path": "petsmart_manual.pdf", 
            "title": "PetSmart Manual"
        }
    ]
    
    # Use the proven ingestion pattern
    client, collection, model = ingest_petsmart_pdfs(pdf_files, "petsmart_documents")
    
    # Show final count
    final_count = collection.count()
    print(f"\nFinal result: {final_count} documents in collection")
    print("Ingestion completed successfully!")