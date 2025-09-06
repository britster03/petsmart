import streamlit as st
import json
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
from typing import Dict, List, Any
import re
from urllib.parse import urlparse

# Page configuration
st.set_page_config(
    page_title="PetSmart RAG Assistant - Demo",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with dark/light theme support
st.markdown("""
<style>
    /* Force light theme */
    .main .block-container {
        background-color: white;
        color: #262730;
    }
    
    /* Override Streamlit's dark theme */
    .stApp {
        background-color: #FFFFFF;
        color: #262730;
    }
    
    /* Main header styling */
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1E88E5;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #1E88E5, #42A5F5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    /* Answer box with subtle styling */
    .answer-box {
        border: 2px solid #4CAF50;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        background: linear-gradient(135deg, #F1F8E9 0%, #E8F5E8 50%, #C8E6C8 100%);
        box-shadow: 0 6px 12px rgba(76, 175, 80, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    /* Add a subtle pattern to answer box */
    .answer-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #4CAF50, #8BC34A, #4CAF50);
    }
    
    /* Answer text styling */
    .answer-box h3 {
        color: #2E7D32;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Link buttons */
    .link-button {
        display: inline-block;
        background: linear-gradient(135deg, #1E88E5, #1976D2);
        color: white;
        padding: 0.7rem 1.2rem;
        border-radius: 8px;
        text-decoration: none;
        margin: 0.3rem;
        font-size: 0.9rem;
        font-weight: 500;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(30, 136, 229, 0.3);
    }
    
    .link-button:hover {
        background: linear-gradient(135deg, #1976D2, #1565C0);
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(30, 136, 229, 0.4);
        color: white;
        text-decoration: none;
    }
    
    /* Metrics cards */
    .metric-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        border-left: 4px solid #1E88E5;
    }
    
    /* Section headers */
    h3 {
        color: #1E88E5;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    /* Expander styling */
    .streamlit-expander {
        border: 1px solid #E0E0E0;
        border-radius: 8px;
        margin-bottom: 0.5rem;
    }
    
    /* Progress bars */
    .stProgress .st-bo {
        background-color: #E3F2FD;
    }
    
    /* Clean up text areas */
    .stTextArea label {
        font-weight: 500;
        color: #424242;
    }
    
    /* Theme toggle info */
    .theme-info {
        background: #E3F2FD;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196F3;
        margin: 1rem 0;
    }
    
    /* Enhanced answer container */
    .answer-container {
        background: linear-gradient(135deg, #E8F5E8 0%, #F1F8E9 100%);
        border-radius: 15px;
        margin: 1.5rem 0;
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.15);
        border: 1px solid #C8E6C8;
        overflow: hidden;
    }
    
    .answer-header {
        background: linear-gradient(135deg, #4CAF50, #66BB6A);
        color: white;
        padding: 1rem 1.5rem;
        margin: 0;
    }
    
    .answer-header h3 {
        margin: 0;
        color: white;
        font-weight: 600;
    }
    
    .answer-content {
        padding: 1.5rem;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #2E7D32;
        font-weight: 500;
    }
    
    /* Beautiful metric cards */
    .metric-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #F0F0F0;
        transition: all 0.3s ease;
        margin: 0.5rem 0;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.12);
    }
    
    .metric-icon {
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Enhanced section headers */
    .section-header {
        background: linear-gradient(135deg, #1E88E5, #42A5F5);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        margin: 2rem 0 1rem 0;
        font-weight: 600;
    }
    
    /* Improved expander styling */
    .chunk-expander {
        background: white;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Clean code blocks */
    .stCode {
        background: #F8F9FA !important;
        border: 1px solid #E9ECEF !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

def load_sample_data():
    """Load sample response data"""
    sample_data = {
        "answer": "To access marketing support materials, you can visit the Partner Resource Center. The US version is available at https://petsmartcharities.org/pro/resources and the Canadian version at https://petsmartcharities.ca/pro/resources. You'll find grant recipient toolkits, brand guidelines, and official logos for both US and Canadian partners.",
        "chunks": [
            {
                "text": "Partner Resource Center US [https://petsmartcharities.org/pro/resources] • Partner Resource Centre Canada [https://petsmartcharities.ca/pro/resources] Marketing Support Links Grant Recipient Toolkit: Use these tools to spread the word about our partnership! Here you'll find graphics, templates, and talking points to help promote your organization's work with PetSmart Charities.",
                "metadata": {
                    "page": 2,
                    "document": "PetSmart Guide",
                    "snippet": "Partner Resource Center US [https://petsmartchari",
                    "pdf_path": "petsmart_guide.pdf",
                    "links_count": 18,
                    "links_json": "[{\"text\": \"Partner Resource Center US\", \"url\": \"https://petsmartcharities.org/pro/resources\"}, {\"text\": \"Partner Resource Centre Canada\", \"url\": \"https://petsmartcharities.ca/pro/resources\"}]"
                },
                "similarity": 0.892
            },
            {
                "text": "US Grant Recipient Toolkit [https://petsmartcharities.org/pro/resources/marketing-support/grant-recipient-toolkit-us] Canadian Grant Recipient Toolkit [https://petsmartcharities.ca/pro/resources/marketing-support/grant-recipient-toolkit-ca] PetSmart Charities US Logos [https://petsmartcharities.org/pro/resources/marketing-support/petsmart-charities-logos] PetSmart Charities Canada Logos [https://petsmartcharities.ca/pro/resources/marketing-support/petsmart-charities-of-canada-logos]",
                "metadata": {
                    "page": 2,
                    "document": "PetSmart Guide", 
                    "snippet": "US Grant Recipient Toolkit [https://petsmartcha",
                    "pdf_path": "petsmart_guide.pdf",
                    "links_count": 18,
                    "links_json": "[{\"text\": \"US Grant Recipient Toolkit\", \"url\": \"https://petsmartcharities.org/pro/resources/marketing-support/grant-recipient-toolkit-us\"}, {\"text\": \"PetSmart Charities US Logos\", \"url\": \"https://petsmartcharities.org/pro/resources/marketing-support/petsmart-charities-logos\"}]"
                },
                "similarity": 0.856
            },
            {
                "text": "US Brand Guidelines [https://petsmartcharities.org/pro/resources/marketing-support/brand-guidelines-for-petsmart-charities] Canadian Brand Guidelines [https://petsmartcharities.ca/pro/resources/marketing-support/brand-guidelines-for-petsmart-charities-of-canada] For questions about marketing support, contact PetSmartCharitiesMarketing@PetSmartCharities.org [mailto:PetSmartCharitiesMarketing@PetSmartCharities.org]",
                "metadata": {
                    "page": 2,
                    "document": "PetSmart Guide",
                    "snippet": "US Brand Guidelines [https://petsmartcharities",
                    "pdf_path": "petsmart_guide.pdf", 
                    "links_count": 18,
                    "links_json": "[{\"text\": \"US Brand Guidelines\", \"url\": \"https://petsmartcharities.org/pro/resources/marketing-support/brand-guidelines-for-petsmart-charities\"}, {\"text\": \"PetSmartCharitiesMarketing@PetSmartCharities.org\", \"url\": \"mailto:PetSmartCharitiesMarketing@PetSmartCharities.org\"}]"
                },
                "similarity": 0.834
            }
        ]
    }
    return sample_data

def extract_links_from_text(text: str) -> List[Dict[str, str]]:
    """Extract URLs from text using regex"""
    # Pattern to match URLs in brackets [url] format and standalone URLs
    url_patterns = [
        r'\[([^\]]+)\]',  # URLs in brackets
        r'https?://[^\s<>"{}|\\^`\[\]]+',  # Standard URLs
        r'mailto:[^\s<>"{}|\\^`\[\]]+',  # Email links
    ]
    
    links = []
    for pattern in url_patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            if match.startswith(('http', 'mailto')):
                links.append({
                    'url': match,
                    'display_text': match
                })
    
    return links

def create_knowledge_graph(query: str, answer: str, chunks: List[Dict]) -> None:
    """Create and display a rich, interactive knowledge graph"""
    st.markdown("### 🕸️ Knowledge Graph Visualization")
    st.markdown("*Explore the relationships between your query, AI response, and source documents*")
    
    nodes = []
    edges = []
    
    # Enhanced visual design with richer elements
    
    # Add query node (center) - enhanced with gradient
    nodes.append(Node(
        id="query",
        label="🔍 Your Query",
        size=60,
        color={"background": "#2196F3", "border": "#1976D2", "highlight": {"background": "#1E88E5", "border": "#1565C0"}},
        shape="dot",
        font={"size": 20, "color": "white", "face": "Segoe UI", "strokeWidth": 2, "strokeColor": "#1976D2"},
        borderWidth=3,
        title=f"🔍 Query: {query}",
        shadow={"enabled": True, "color": "rgba(33, 150, 243, 0.3)", "size": 10}
    ))
    
    # Add answer node - enhanced with rich styling
    nodes.append(Node(
        id="answer",
        label="🤖 AI Response",
        size=55,
        color={"background": "#4CAF50", "border": "#388E3C", "highlight": {"background": "#66BB6A", "border": "#2E7D32"}},
        shape="dot",
        font={"size": 18, "color": "white", "face": "Segoe UI", "strokeWidth": 2, "strokeColor": "#2E7D32"},
        borderWidth=3,
        title=f"🤖 AI Response: {answer[:150]}...",
        shadow={"enabled": True, "color": "rgba(76, 175, 80, 0.3)", "size": 10}
    ))
    
    # Connect query to answer with animated styling
    edges.append(Edge(
        source="query",
        target="answer",
        color={"color": "#4CAF50", "opacity": 0.9},
        width=5,
        smooth={"type": "dynamic", "roundness": 0.5},
        label="generates",
        font={"size": 14, "color": "#2E7D32", "face": "Segoe UI", "strokeWidth": 1, "strokeColor": "white"},
        arrows={"to": {"enabled": True, "scaleFactor": 1.2}}
    ))
    
    # Enhanced chunk nodes with rich details
    chunk_configs = [
        {"color": "#FF9800", "border": "#F57C00", "icon": "📗", "name": "Guide"},
        {"color": "#9C27B0", "border": "#7B1FA2", "icon": "📘", "name": "Manual"}, 
        {"color": "#607D8B", "border": "#455A64", "icon": "📄", "name": "Doc"}
    ]
    
    for i, chunk in enumerate(chunks[:3]):
        chunk_id = f"chunk_{i}"
        
        # Extract enhanced document info
        document = chunk.get("metadata", {}).get("document", "Unknown")
        page = chunk.get("metadata", {}).get("page", "?")
        similarity = chunk.get("similarity", 0)
        links_count = len(extract_links_from_text(chunk.get("text", "")))
        
        config = chunk_configs[i % len(chunk_configs)]
        doc_type = "Guide" if "Guide" in document else "Manual" if "Manual" in document else "Doc"
        
        nodes.append(Node(
            id=chunk_id,
            label=f"{config['icon']} {doc_type}\nPage {page}\n⭐ {similarity:.2f}",
            size=45,
            color={
                "background": config["color"], 
                "border": config["border"],
                "highlight": {"background": config["color"], "border": config["border"]}
            },
            shape="dot",
            font={"size": 13, "color": "white", "face": "Segoe UI", "strokeWidth": 1, "strokeColor": config["border"]},
            borderWidth=2,
            title=f"{config['icon']} Document: {document}\n📄 Page: {page}\n⭐ Similarity: {similarity:.3f}\n🔗 Links: {links_count}",
            shadow={"enabled": True, "color": f"{config['color']}40", "size": 8}
        ))
        
        # Enhanced edge with similarity-based styling
        edge_width = max(3, int(similarity * 8))
        edge_opacity = 0.6 + (similarity * 0.4)
        
        edges.append(Edge(
            source=chunk_id,
            target="answer",
            color={"color": config["color"], "opacity": edge_opacity},
            width=edge_width,
            smooth={"type": "dynamic", "roundness": 0.3},
            label=f"supports ({similarity:.2f})",
            font={"size": 11, "color": config["border"], "face": "Segoe UI"},
            arrows={"to": {"enabled": True, "scaleFactor": 1.0}}
        ))
        
        # Enhanced link nodes with better categorization
        chunk_text = chunk.get("text", "")
        links = extract_links_from_text(chunk_text)
        
        for j, link in enumerate(links[:2]):
            link_id = f"link_{i}_{j}"
            
            # Enhanced link categorization with icons
            if link["url"].startswith("http"):
                domain = urlparse(link["url"]).netloc
                if "petsmartcharities" in domain:
                    icon, label = "🏢", "PetSmart Portal"
                elif "facebook" in domain:
                    icon, label = "📘", "Facebook"
                elif "instagram" in domain:
                    icon, label = "📸", "Instagram"
                elif "youtube" in domain:
                    icon, label = "📺", "YouTube"
                else:
                    icon, label = "🌐", domain.replace("www.", "")
            else:
                icon, label = "📧", "Email"
            
            nodes.append(Node(
                id=link_id,
                label=f"{icon}\n{label}",
                size=30,
                color={
                    "background": "#FFC107", 
                    "border": "#FF8F00",
                    "highlight": {"background": "#FFD54F", "border": "#FF6F00"}
                },
                shape="box",
                font={"size": 11, "color": "#E65100", "face": "Segoe UI", "strokeWidth": 1, "strokeColor": "#FF8F00"},
                borderWidth=2,
                title=f"{icon} {label}\n🔗 {link['url']}",
                shadow={"enabled": True, "color": "rgba(255, 193, 7, 0.3)", "size": 6}
            ))
            
            edges.append(Edge(
                source=chunk_id,
                target=link_id,
                color={"color": "#FFC107", "opacity": 0.7},
                width=2,
                smooth={"type": "continuous"},
                dashes=[8, 4],
                label="links to",
                font={"size": 10, "color": "#FF8F00", "face": "Segoe UI"},
                arrows={"to": {"enabled": True, "scaleFactor": 0.8}}
            ))
    
    # Fixed graph configuration with only valid vis.js options
    graph_config = Config(
        width=900,
        height=600,
        directed=True,
        hierarchical=False,
        
        # Valid physics configuration
        physics=True,
        
        # Valid interaction options
        interaction={
            "dragNodes": True,
            "dragView": True,
            "zoomView": True,
            "hover": True,
            "hoverConnectedEdges": True,
            "selectConnectedEdges": True
        },
        
        # Valid layout options
        layout={
            "improvedLayout": True,
            "randomSeed": 42
        },
        
        # Valid edge styling
        edges={
            "smooth": {"enabled": True, "type": "dynamic"},
            "arrows": {"to": {"enabled": True}}
        }
    )
    
    # Display with enhanced spacing and container
    st.markdown("""
    <div style="background: white; padding: 1rem; border-radius: 12px; box-shadow: 0 4px 16px rgba(0,0,0,0.1); margin: 1rem 0;">
    """, unsafe_allow_html=True)
    
    selected_node = agraph(nodes=nodes, edges=edges, config=graph_config)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if selected_node:
        st.success(f"🎯 Selected Node: **{selected_node}**")
        
    # Enhanced legend with better design
    st.markdown("""
    <div style="background: linear-gradient(135deg, #F8F9FA 0%, #E9ECEF 100%); padding: 1.5rem; border-radius: 12px; margin-top: 1rem; border-left: 4px solid #2196F3;">
        <h4 style="color: #1976D2; margin-top: 0; display: flex; align-items: center;">
            🗺️ Interactive Graph Legend
        </h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1rem;">
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: #2196F3; border-radius: 50%; display: inline-block; box-shadow: 0 2px 4px rgba(33,150,243,0.3);"></span>
                <span><strong>Your Query</strong> - Starting point</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: #4CAF50; border-radius: 50%; display: inline-block; box-shadow: 0 2px 4px rgba(76,175,80,0.3);"></span>
                <span><strong>AI Answer</strong> - Generated response</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 20px; background: #FF9800; border-radius: 50%; display: inline-block; box-shadow: 0 2px 4px rgba(255,152,0,0.3);"></span>
                <span><strong>Source Docs</strong> - Knowledge base</span>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem;">
                <span style="width: 20px; height: 15px; background: #FFC107; border-radius: 3px; display: inline-block; box-shadow: 0 2px 4px rgba(255,193,7,0.3);"></span>
                <span><strong>External Links</strong> - Resources</span>
            </div>
        </div>
        <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #DEE2E6; font-size: 0.9rem; color: #6C757D;">
            💡 <strong>Pro Tip:</strong> Hover over nodes for detailed information, drag to rearrange, and click to select elements.
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 PetSmart RAG Assistant - Demo</h1>', unsafe_allow_html=True)
    
    st.markdown("### 🎮 Interactive Demo")
    st.markdown("""
    <div style="background-color: #000000; color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
        This is a demo version showing how the interface works with sample data. Connect your Langflow API to make it fully functional!
    </div>
    """, unsafe_allow_html=True)
    
    # Simple collapsible design guide
    with st.expander("🎨 Interface Design Guide", expanded=False):
        st.write("**🎯 Design Philosophy**")
        st.write("Our interface combines clarity with functionality to provide an intuitive RAG experience.")
        
        st.write("**🎨 Key Features:**")
        st.write("• 🟢 **Green Answer Box:** Highlights the main RAG response")
        st.write("• 🕸️ **Knowledge Graph:** Interactive visualization of relationships") 
        st.write("• 📊 **Metric Cards:** Beautiful analytics with hover effects")
        st.write("• 🔗 **Smart Links:** All extracted hyperlinks are preserved")
        
        st.write("**🎯 Color System:**")
        st.write("• 🔵 **Blue:** User queries and primary actions")
        st.write("• 🟢 **Green:** AI-generated answers and success states") 
        st.write("• 🟠 **Orange:** PetSmart Guide content")
        st.write("• 🟣 **Purple:** PetSmart Manual content")
        st.write("• 🟨 **Yellow:** External links and resources")
    
    # Load sample data
    sample_data = load_sample_data()
    query = "How can I access marketing support materials and brand guidelines?"
    
    # Display query with better visibility  
    st.markdown("### 🔍 Sample Query")
    st.markdown(f"""
    <div style="background: #1E3A8A !important; color: white !important; padding: 1.5rem; border-radius: 8px; font-family: 'Courier New', monospace; font-size: 1.2rem; margin: 1rem 0; font-weight: 500; border: 2px solid #3B82F6; -webkit-text-fill-color: white !important;">
        <span style="color: white !important;">{query}</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Main answer section with enhanced styling
    st.markdown("""
    <div class="answer-container">
        <div class="answer-header">
            <h3>🎯 AI Assistant Response</h3>
        </div>
        <div class="answer-content">
    """ + sample_data.get("answer", "No answer provided") + """
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Enhanced metrics section
    chunks = sample_data.get("chunks", [])
    links_found = 0
    for chunk in chunks:
        links_found += len(extract_links_from_text(chunk.get("text", "")))
    
    avg_similarity = sum(chunk.get("similarity", 0) for chunk in chunks) / len(chunks) if chunks else 0
    documents = set(chunk.get("metadata", {}).get("document", "Unknown") for chunk in chunks)
    
    # Beautiful metrics cards
    st.markdown("### 📊 Response Analytics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">📄</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Source Chunks</div>
        </div>
        """.format(len(chunks)), unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">📚</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Documents</div>
        </div>
        """.format(len(documents)), unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">🔗</div>
            <div class="metric-value">{}</div>
            <div class="metric-label">Links Found</div>
        </div>
        """.format(links_found), unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-icon">🎯</div>
            <div class="metric-value">{:.3f}</div>
            <div class="metric-label">Avg Similarity</div>
        </div>
        """.format(avg_similarity), unsafe_allow_html=True)
    
    # Create two columns for main content
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        # Knowledge Graph
        answer = sample_data.get("answer", "No answer provided")
        create_knowledge_graph(query, answer, chunks)
    
    with col_right:
        # Source chunks details with enhanced styling
        st.markdown('<div class="section-header">📄 Source Chunks</div>', unsafe_allow_html=True)
        
        for i, chunk in enumerate(chunks[:3]):  # Show fewer chunks for cleaner view
            document = chunk.get('metadata', {}).get('document', 'Unknown')
            page = chunk.get('metadata', {}).get('page', '?')
            similarity = chunk.get("similarity", 0)
            
            # Clean document name for display
            doc_display = "📗 Guide" if "Guide" in document else "📘 Manual" if "Manual" in document else "📄 Document"
            
            with st.expander(f"{doc_display} - Page {page} (Similarity: {similarity:.3f})"):
                
                # Chunk content with better formatting
                chunk_text = chunk.get("text", "")
                st.markdown("**📝 Content Preview:**")
                
                # Show a clean preview
                preview_text = chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text
                st.markdown(f'<div style="background: #F8F9FA; padding: 1rem; border-radius: 6px; border-left: 3px solid #1E88E5; font-family: monospace; font-size: 0.9rem;">{preview_text}</div>', unsafe_allow_html=True)
                
                # Similarity visualization
                st.markdown("**🎯 Relevance Score:**")
                progress_color = "#4CAF50" if similarity > 0.8 else "#FF9800" if similarity > 0.6 else "#FF5722"
                st.markdown(f'''
                <div style="background: #F5F5F5; border-radius: 10px; padding: 0.5rem;">
                    <div style="background: {progress_color}; width: {similarity*100}%; height: 8px; border-radius: 4px;"></div>
                    <small style="color: #666;">Score: {similarity:.3f} ({similarity*100:.1f}%)</small>
                </div>
                ''', unsafe_allow_html=True)
                
                # Extract and display links with better styling
                links = extract_links_from_text(chunk_text)
                if links:
                    st.markdown("**🔗 Available Links:**")
                    links_html = ""
                    for link in links[:3]:  # Limit to 3 links
                        if link["url"].startswith("http"):
                            link_text = link["url"].split("/")[-1] if "/" in link["url"] else link["url"]
                            links_html += f'<a href="{link["url"]}" target="_blank" class="link-button" style="margin: 0.2rem; display: inline-block;">🌐 {link_text[:20]}...</a>'
                        elif link["url"].startswith("mailto"):
                            links_html += f'<a href="{link["url"]}" class="link-button" style="margin: 0.2rem; display: inline-block;">📧 Email</a>'
                    
                    st.markdown(links_html, unsafe_allow_html=True)
                else:
                    st.markdown("*No external links in this chunk*")
                
                # Quick metadata
                st.markdown("**ℹ️ Details:**")
                st.markdown(f"• **Source:** {document}")
                st.markdown(f"• **Page:** {page}")
                st.markdown(f"• **Length:** {len(chunk_text)} characters")
    
    # Enhanced insights section
    st.markdown('<div class="section-header">📊 Response Analysis</div>', unsafe_allow_html=True)
    
    # Create two columns for analysis
    analysis_col1, analysis_col2 = st.columns(2)
    
    with analysis_col1:
        st.markdown("**📚 Document Usage Distribution**")
        
        # Document distribution with better visualization
        doc_counts = {}
        for chunk in chunks:
            doc = chunk.get("metadata", {}).get("document", "Unknown")
            doc_counts[doc] = doc_counts.get(doc, 0) + 1
        
        if doc_counts:
            # Create a nice donut chart representation
            total_chunks = sum(doc_counts.values())
            for doc, count in doc_counts.items():
                percentage = (count / total_chunks) * 100
                doc_emoji = "📗" if "Guide" in doc else "📘"
                st.markdown(f"""
                <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #1E88E5;">
                    <strong>{doc_emoji} {doc}</strong><br>
                    <span style="font-size: 1.2rem; color: #1E88E5;">{count} chunks</span> 
                    <span style="color: #666;">({percentage:.1f}%)</span>
                </div>
                """, unsafe_allow_html=True)
    
    with analysis_col2:
        st.markdown("**🔗 Link Categories Summary**")
        
        # All extracted links with categorization
        all_links = []
        for chunk in chunks:
            all_links.extend(extract_links_from_text(chunk.get("text", "")))
        
        if all_links:
            # Categorize links
            categories = {
                "🏢 Resources": 0,
                "📧 Contact": 0, 
                "📱 Social": 0,
                "🌐 Other": 0
            }
            
            for link in all_links:
                url = link["url"].lower()
                if "resources" in url or "toolkit" in url:
                    categories["🏢 Resources"] += 1
                elif "mailto:" in url:
                    categories["📧 Contact"] += 1
                elif any(social in url for social in ["facebook", "instagram", "twitter", "youtube"]):
                    categories["📱 Social"] += 1
                else:
                    categories["🌐 Other"] += 1
            
            for category, count in categories.items():
                if count > 0:
                    st.markdown(f"""
                    <div style="background: white; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; border-left: 4px solid #FFC107;">
                        <strong>{category}</strong><br>
                        <span style="font-size: 1.2rem; color: #FFC107;">{count} links</span>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Expandable detailed links section
    if all_links:
        with st.expander(f"🔗 View All {len(all_links)} Extracted Links", expanded=False):
            # Group links by domain for better organization
            domain_links = {}
            for link in all_links:
                if link["url"].startswith("http"):
                    domain = urlparse(link["url"]).netloc
                    if "petsmartcharities" in domain:
                        domain = "PetSmart Charities Portal"
                    elif "facebook" in domain:
                        domain = "Facebook"
                    elif "instagram" in domain:
                        domain = "Instagram"
                    elif "twitter" in domain:
                        domain = "Twitter"
                    elif "youtube" in domain:
                        domain = "YouTube"
                    else:
                        domain = domain.replace("www.", "")
                else:
                    domain = "📧 Email Contacts"
                
                if domain not in domain_links:
                    domain_links[domain] = []
                domain_links[domain].append(link)
            
            # Display grouped links with better formatting
            for domain, links in domain_links.items():
                st.markdown(f"**🌐 {domain}** ({len(links)} links)")
                for link in links:
                    st.markdown(f'• <a href="{link["url"]}" target="_blank" style="color: #1E88E5; text-decoration: none;">{link["url"]}</a>', unsafe_allow_html=True)
                st.markdown("---")
    
    # Instructions for real usage
    st.markdown("---")
    st.markdown("### 🚀 To Use With Your Langflow API:")
    st.markdown("""
    1. **Replace the demo data**: Update the `call_langflow_api()` function in `streamlit_app.py`
    2. **Configure your API**: Enter your Langflow API URL in the sidebar
    3. **Adjust the response format**: Ensure your Langflow returns data in this structure:
    ```json
    {
        "answer": "Your generated answer",
        "chunks": [
            {
                "text": "Chunk content with embedded URLs [https://example.com]",
                "metadata": {
                    "page": 1,
                    "document": "Document Name",
                    "links_count": 5
                },
                "similarity": 0.95
            }
        ]
    }
    ```
    """)
    
    # Debug section
    with st.expander("🔧 Sample API Response Structure"):
        st.json(sample_data)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; margin-top: 2rem;">
            <p>🐾 PetSmart RAG Assistant Demo | Powered by Langflow & Streamlit</p>
            <p>Built with ❤️ for PetSmart Adoption Partners</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
