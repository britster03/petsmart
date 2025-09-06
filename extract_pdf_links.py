import fitz  # PyMuPDF
import json

def extract_links_from_pdf(pdf_path):
    """Extract all hyperlinks from a PDF file"""
    print(f"🔍 Extracting hyperlinks from {pdf_path}")
    
    doc = fitz.open(pdf_path)
    all_links = []
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Get all links on this page
        links = page.get_links()
        
        if links:
            print(f"\n📄 Page {page_num + 1} - Found {len(links)} links:")
            
            for link in links:
                link_info = {
                    'page': page_num + 1,
                    'type': link.get('kind', 'unknown'),
                    'rect': link.get('from', None),  # Rectangle coordinates
                    'uri': link.get('uri', None),    # The actual URL
                    'title': link.get('title', None) # Link title if any
                }
                
                # Get the text that's being linked (the blue text)
                if 'from' in link:
                    rect = fitz.Rect(link['from'])
                    # Extract text from the link rectangle
                    link_text = page.get_textbox(rect).strip()
                    link_info['display_text'] = link_text
                
                all_links.append(link_info)
                
                # Print link details
                print(f"  🔗 Link: {link_info.get('display_text', 'No text')}")
                print(f"     → URL: {link_info.get('uri', 'No URI')}")
                if link_info.get('title'):
                    print(f"     → Title: {link_info['title']}")
                print()
        else:
            print(f"\n📄 Page {page_num + 1} - No links found")
    
    doc.close()
    return all_links

def extract_text_with_links(pdf_path):
    """Extract text while preserving link information"""
    print(f"\n📝 Extracting text with embedded link information from {pdf_path}")
    
    doc = fitz.open(pdf_path)
    pages_with_links = []
    
    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        
        # Get the text
        text = page.get_text("text")
        
        # Get links
        links = page.get_links()
        
        # Create enhanced text with link URLs embedded
        enhanced_text = text
        link_mapping = {}
        
        for link in links:
            if 'from' in link and 'uri' in link:
                rect = fitz.Rect(link['from'])
                link_text = page.get_textbox(rect).strip()
                uri = link['uri']
                
                if link_text and uri:
                    # Replace the link text with text + URL
                    enhanced_link = f"{link_text} [{uri}]"
                    enhanced_text = enhanced_text.replace(link_text, enhanced_link)
                    link_mapping[link_text] = uri
        
        page_info = {
            'page': page_num + 1,
            'original_text': text,
            'enhanced_text': enhanced_text,
            'links': link_mapping
        }
        
        pages_with_links.append(page_info)
        
        if link_mapping:
            print(f"\n📄 Page {page_num + 1} enhanced with {len(link_mapping)} links")
            for display_text, url in link_mapping.items():
                print(f"  '{display_text}' → {url}")
    
    doc.close()
    return pages_with_links

def compare_extraction_methods(pdf_path):
    """Compare different text extraction methods"""
    print(f"\n🔬 Comparing extraction methods for {pdf_path}")
    
    doc = fitz.open(pdf_path)
    
    for page_num in range(min(3, doc.page_count)):  # Check first 3 pages
        page = doc.load_page(page_num)
        
        print(f"\n📄 Page {page_num + 1}:")
        print("-" * 50)
        
        # Method 1: Plain text
        text_plain = page.get_text("text")
        print("Plain text extraction:")
        print(text_plain[:300] + "..." if len(text_plain) > 300 else text_plain)
        
        # Method 2: HTML (preserves some link info)
        try:
            text_html = page.get_text("html")
            print(f"\nHTML extraction (first 500 chars):")
            print(text_html[:500] + "..." if len(text_html) > 500 else text_html)
        except:
            print("\nHTML extraction failed")
        
        # Method 3: Links
        links = page.get_links()
        print(f"\nDirect link extraction: {len(links)} links found")
        for i, link in enumerate(links[:3]):  # Show first 3 links
            print(f"  Link {i+1}: {link}")
    
    doc.close()

if __name__ == "__main__":
    pdf_path = "petsmart_guide.pdf"
    
    print("🚀 PetSmart Guide PDF Link Extraction Analysis")
    print("=" * 60)
    
    # 1. Extract all hyperlinks
    all_links = extract_links_from_pdf(pdf_path)
    
    # 2. Show summary
    print(f"\n📊 Summary:")
    print(f"Total links found: {len(all_links)}")
    
    if all_links:
        unique_domains = set()
        for link in all_links:
            uri = link.get('uri', '')
            if uri:
                if '://' in uri:
                    domain = uri.split('://')[1].split('/')[0]
                else:
                    domain = uri.split('/')[0]
                unique_domains.add(domain)
        
        print(f"Unique domains: {len(unique_domains)}")
        print("Domains found:")
        for domain in sorted(unique_domains):
            print(f"  • {domain}")
        
        # Save to JSON for analysis
        with open('extracted_links.json', 'w') as f:
            json.dump(all_links, f, indent=2)
        print(f"\n💾 Detailed link data saved to 'extracted_links.json'")
    
    # 3. Compare extraction methods
    compare_extraction_methods(pdf_path)
    
    # 4. Extract enhanced text with links
    enhanced_pages = extract_text_with_links(pdf_path)
    
    print(f"\n✅ Analysis complete!")
