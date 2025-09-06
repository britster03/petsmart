import streamlit as st
import requests
import json
from streamlit_agraph import agraph, Node, Edge, Config
import pandas as pd
from typing import Dict, List, Any
import re
from urllib.parse import urlparse
import time
import chromadb
import os

# Page configuration
st.set_page_config(
    page_title="PetSmart RAG Assistant",
    page_icon="🐾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS with professional styling
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
        font-size: 1.2rem;
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
    
    /* Clean code blocks */
    .stCode {
        background: #F8F9FA !important;
        border: 1px solid #E9ECEF !important;
        border-radius: 8px !important;
    }
    
    /* White text for sample queries */
    .sample-queries {
        color: white !important;
    }
    
    /* More specific selector for sample queries */
    .stMarkdown .sample-queries,
    .stMarkdown .sample-queries p,
    .stMarkdown .sample-queries strong {
        color: white !important;
    }
    
    /* Force white text with highest specificity */
    div[data-testid="stMarkdownContainer"] p[style*="color: white"],
    div[data-testid="stMarkdownContainer"] p[style*="color: white"] strong,
    .main .block-container p[style*="color: white"],
    .main .block-container p[style*="color: white"] strong {
        color: white !important;
    }
    
    /* White text for sample query buttons */
    .stButton > button {
        color: white !important;
        background-color: rgba(0, 0, 0, 0.7) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
    }
    
    .stButton > button:hover {
        color: white !important;
        background-color: rgba(0, 0, 0, 0.9) !important;
        border: 1px solid rgba(255, 255, 255, 0.5) !important;
    }
    
    /* Black text for success messages */
    .stSuccess {
        color: black !important;
    }
    
    .stSuccess > div {
        color: black !important;
    }
    
    .stSuccess div[data-testid="stMarkdownContainer"] {
        color: black !important;
    }
</style>
""", unsafe_allow_html=True)

class PetSmartRAGInterface:
    def __init__(self):
        self.api_url = None
        self.response_data = None
        
    def setup_sidebar(self):
        """Setup the sidebar with configuration options"""
        st.sidebar.markdown("## 🔧 Configuration")
        
        # API URL input
        self.api_url = st.sidebar.text_input(
            "Langflow API URL",
            placeholder="https://langflows.vercel.app/api/v1/run/957834e3-c519-40ea-a494-4f732a882d28",
            help="Enter the API endpoint for your Langflow",
            value="https://langflows.vercel.app/api/v1/run/957834e3-c519-40ea-a494-4f732a882d28"
        )
        
        # API Key input
        api_key = st.sidebar.text_input(
            "Langflow API Key",
            placeholder="sk-...",
            help="Enter your Langflow API key",
            type="password",
            value="sk-wYgAQ3w9IZlhOBBhrzuuqLpyfmVWLSZk2QHOMlVYZgo"
        )
        
        # Store API key in session state
        if api_key:
            st.session_state['langflow_api_key'] = api_key
        
        return {
            "graph_physics": True,
            "graph_hierarchical": False,
            "graph_width": 900,
            "graph_height": 600,
            "show_metadata": True,
            "show_links": True,
            "max_chunks_display": 3
        }
    
    def petsmart_query(self, user_query: str) -> Dict[str, Any]:
        try:
            with st.spinner("🤖 Processing your query..."):
                # ChromaDB query
                client = chromadb.CloudClient(
                    api_key='ck-GbrLBVwv1NppMUTvq38k5MwMxinBaRtaa6oyAiAFxHDN',
                    tenant='986f4b43-03a2-4f26-a81f-311f83dff543',
                    database='petsmart'
                )
                collection = client.get_or_create_collection(name="petsmart_documents")
                chroma_results = collection.query(
                    query_texts=[user_query],
                    n_results=10
                )

                # Langflow API call
                api_key = "sk-wYgAQ3w9IZlhOBBhrzuuqLpyfmVWLSZk2QHOMlVYZgo"
                os.environ["LANGFLOW_API_KEY"] = api_key
                url = "https://langflows.vercel.app/api/v1/run/957834e3-c519-40ea-a494-4f732a882d28"

                payload = {
                    "input_value": user_query,
                    "output_type": "chat",
                    "input_type": "chat"
                }

                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": api_key
                }

                response = requests.post(url, json=payload, headers=headers)
                data = json.loads(response.text)
                api_answer = data["outputs"][0]["outputs"][0]["artifacts"]["message"]

                # Build chunks
                chunks = []
                for i in range(len(chroma_results['documents'][0])):
                    chunk = {
                        'text': chroma_results['documents'][0][i],
                        'metadata': {
                            'page': chroma_results['metadatas'][0][i].get('page', 'N/A'),
                            'document': chroma_results['metadatas'][0][i].get('document', 'Unknown'),
                            'snippet': chroma_results['metadatas'][0][i].get('snippet', '')[:50] + '...',
                            'pdf_path': chroma_results['metadatas'][0][i].get('pdf_path', ''),
                            'links_count': chroma_results['metadatas'][0][i].get('links_count', 0),
                            'links_json': chroma_results['metadatas'][0][i].get('links_json', '[]')
                        },
                        'similarity': round(1 - (chroma_results['distances'][0][i] / 2), 3)
                    }
                    chunks.append(chunk)

                # Merged response
                result = {
                    'answer': api_answer,
                    'chunks': chunks
                }

                return result
                
        except Exception as e:
            st.error(f"Error in petsmart_query: {str(e)}")
            return None

    def call_langflow_api(self, query: str) -> Dict[str, Any]:
        """Wrapper to use the working petsmart_query function"""
        return self.petsmart_query(query)
    
    def extract_links_from_text(self, text: str) -> List[Dict[str, str]]:
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
    
    def create_knowledge_graph(self, query: str, answer: str, chunks: List[Dict], config: Dict) -> None:
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
            links_count = len(self.extract_links_from_text(chunk.get("text", "")))
            
            config_item = chunk_configs[i % len(chunk_configs)]
            doc_type = "Guide" if "Guide" in document else "Manual" if "Manual" in document else "Doc"
            
            nodes.append(Node(
                id=chunk_id,
                label=f"{config_item['icon']} {doc_type}\nPage {page}",
                size=45,
                color={
                    "background": config_item["color"], 
                    "border": config_item["border"],
                    "highlight": {"background": config_item["color"], "border": config_item["border"]}
                },
                shape="dot",
                font={"size": 13, "color": "white", "face": "Segoe UI", "strokeWidth": 1, "strokeColor": config_item["border"]},
                borderWidth=2,
                title=f"{config_item['icon']} Document: {document}\n📄 Page: {page}\n🔗 Links: {links_count}",
                shadow={"enabled": True, "color": f"{config_item['color']}40", "size": 8}
            ))
            
            # Enhanced edge with similarity-based styling
            edge_width = max(3, int(similarity * 8))
            edge_opacity = 0.6 + (similarity * 0.4)
            
            edges.append(Edge(
                source=chunk_id,
                target="answer",
                color={"color": config_item["color"], "opacity": 0.8},
                width=4,
                smooth={"type": "continuous", "roundness": 0.3},
                label="supports",
                font={"size": 11, "color": config_item["border"], "face": "Segoe UI"},
                arrows={"to": {"enabled": True, "scaleFactor": 1.0}}
            ))
            
            # Enhanced link nodes with better categorization
            chunk_text = chunk.get("text", "")
            links = self.extract_links_from_text(chunk_text)
            
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
        
        # Enhanced graph configuration for cleaner, more spread out layout
        graph_config = Config(
            width=config["graph_width"],
            height=config["graph_height"],
            directed=True,
            hierarchical=False,
            
            # Disable physics for cleaner positioning
            physics=False,
            
            # Valid interaction options
            interaction={
                "dragNodes": True,
                "dragView": True,
                "zoomView": True,
                "hover": True,
                "hoverConnectedEdges": True,
                "selectConnectedEdges": True
            },
            
            # Enhanced layout for better spacing
            layout={
                "improvedLayout": True,
                "randomSeed": 42,
                "clusterThreshold": 150
            },
            
            # Cleaner edge styling
            edges={
                "smooth": {"enabled": True, "type": "continuous", "roundness": 0.2},
                "arrows": {"to": {"enabled": True, "scaleFactor": 1}},
                "length": 200
            },
            
            # Add nodes configuration for better spacing
            nodes={
                "borderWidth": 2,
                "borderWidthSelected": 3,
                "font": {"strokeWidth": 2},
                "margin": 20
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
    
    def display_response(self, query: str, response_data: Dict, config: Dict):
        """Display the RAG response exactly like the demo app"""
        
        # Main answer section with enhanced styling
        answer = response_data.get("answer", "No answer provided")
        st.markdown("""
        <div class="answer-container">
            <div class="answer-header">
                <h3>🎯 AI Assistant Response</h3>
            </div>
            <div class="answer-content">
        """ + answer + """
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Enhanced metrics section
        chunks = response_data.get("chunks", [])
        links_found = 0
        for chunk in chunks:
            links_found += len(self.extract_links_from_text(chunk.get("text", "")))
        
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
            self.create_knowledge_graph(query, answer, chunks, config)
        
        with col_right:
            # Source chunks details with enhanced styling
            st.markdown('<div class="section-header">📄 Source Chunks</div>', unsafe_allow_html=True)
            
            for i, chunk in enumerate(chunks[:3]):  # Show fewer chunks for cleaner view
                document = chunk.get('metadata', {}).get('document', 'Unknown')
                page = chunk.get('metadata', {}).get('page', '?')
                similarity = chunk.get("similarity", 0)
                
                # Clean document name for display
                doc_display = "📗 Guide" if "Guide" in document else "📘 Manual" if "Manual" in document else "📄 Document"
                
                with st.expander(f"{doc_display} - Page {page}"):
                    
                    # Chunk content with better formatting
                    chunk_text = chunk.get("text", "")
                    st.markdown("**📝 Content Preview:**")
                    
                    # Show a clean preview
                    preview_text = chunk_text[:300] + "..." if len(chunk_text) > 300 else chunk_text
                    st.markdown(f'<div style="background: #F8F9FA; padding: 1rem; border-radius: 6px; border-left: 3px solid #1E88E5; font-family: monospace; font-size: 0.9rem;">{preview_text}</div>', unsafe_allow_html=True)
                    
                    
                    # Extract and display links with better styling
                    links = self.extract_links_from_text(chunk_text)
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
                all_links.extend(self.extract_links_from_text(chunk.get("text", "")))
            
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
                        domain = self.extract_domain(link["url"])
                    else:
                        domain = "📧 Email Contacts"
                    
                    if domain not in domain_links:
                        domain_links[domain] = []
                    domain_links[domain].append(link)
                
                # Display grouped links
                for domain, links in domain_links.items():
                    st.markdown(f"**{domain}** ({len(links)} links)")
                    for link in links:
                        st.markdown(f'• <a href="{link["url"]}" target="_blank">{link["url"]}</a>', unsafe_allow_html=True)
                    st.markdown("---")
    
    def extract_domain(self, url):
        """Extract and clean domain name"""
        from urllib.parse import urlparse
        domain = urlparse(url).netloc
        if "petsmartcharities" in domain:
            return "PetSmart Charities Portal"
        elif "facebook" in domain:
            return "Facebook"
        elif "instagram" in domain:
            return "Instagram"
        elif "twitter" in domain:
            return "Twitter"
        elif "youtube" in domain:
            return "YouTube"
        else:
            return domain.replace("www.", "")

def main():
    # Header
    st.markdown('<h1 class="main-header">🐾 PetSmart RAG Assistant</h1>', unsafe_allow_html=True)
    
    # Initialize the interface
    rag_interface = PetSmartRAGInterface()
    
    # Setup sidebar
    config = rag_interface.setup_sidebar()
    
    # Main query interface
    st.markdown("### 🔍 Ask your question about PetSmart resources")
    
    # Query input
    query = st.text_input(
        "Enter your question:",
        placeholder="e.g., How do I apply for a transport grant?",
        help="Ask anything about PetSmart adoption partnerships, grants, resources, etc."
    )
    
    # Sample queries
    st.markdown('''
    <div style="background-color: rgba(0,0,0,0.3); padding: 10px; border-radius: 5px; margin: 10px 0;">
        <p style="color: white !important; margin: 0;"><strong style="color: white !important;">💡 Try these sample queries:</strong></p>
    </div>
    ''', unsafe_allow_html=True)
    sample_queries = [
        "How do I access the Partner Resource Center?",
        "What grants are available for adoption events?",
        "Where can I find marketing support materials?",
        "How do I contact PetSmart Charities?",
        "What are the brand guidelines for partners?"
    ]
    
    cols = st.columns(len(sample_queries))
    for i, sample_query in enumerate(sample_queries):
        with cols[i % len(cols)]:
            if st.button(f"📝 {sample_query[:20]}...", key=f"sample_{i}"):
                query = sample_query
                st.rerun()
    
    # Process query button
    if st.button("🚀 Get Answer", type="primary", disabled=not query):
        if not rag_interface.api_url:
            st.markdown("""
            <div style="background-color: #000000; color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                Please configure the Langflow API URL in the sidebar first!
            </div>
            """, unsafe_allow_html=True)
        else:
            # Call the API
            response_data = rag_interface.call_langflow_api(query)
            
            if response_data:
                
                # Store response for reuse
                rag_interface.response_data = response_data
                
                # Display the response
                rag_interface.display_response(query, response_data, config)
            else:
                st.error("❌ Failed to get response from Langflow API")
    
    # Debug section
    with st.expander("🔧 Debug: API Response (for development)"):
        if rag_interface.response_data:
            st.json(rag_interface.response_data)
        else:
            st.markdown("""
            <div style="background-color: #000000; color: white; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0;">
                No response data yet. Make a query first.
            </div>
            """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; color: #666; margin-top: 2rem;">
            <p>🐾 PetSmart RAG Assistant | Powered by Langflow & Streamlit</p>
            <p>Built with ❤️ for PetSmart Adoption Partners</p>
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
