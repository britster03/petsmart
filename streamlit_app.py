# Simple PetSmart RAG Assistant - Clean UI for Proof of Concept
import sys
import sqlite3

# Check SQLite version and use pysqlite3 if needed
if sqlite3.sqlite_version_info < (3, 35, 0):
    try:
        import pysqlite3 as sqlite3
        sys.modules['sqlite3'] = sqlite3
    except ImportError:
        pass

import streamlit as st
import requests
import json
import chromadb
import os
import re

# Page configuration
st.set_page_config(
    page_title="PetSmart RAG Assistant",
    page_icon="🐾",
    layout="centered"
)

# Minimal clean CSS with black text
st.markdown("""
<style>
    /* Force white background and black text */
    .stApp {
        background-color: white !important;
        color: black !important;
    }
    
    .main .block-container {
        max-width: 700px;
        padding-top: 2rem;
        padding-bottom: 2rem;
        background-color: white !important;
        color: black !important;
    }
    
    /* Force all text to be black */
    .main .block-container * {
        color: black !important;
    }
    
    .header {
        text-align: center;
        color: #1E88E5 !important;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 2rem;
    }
    
    .answer-box {
        background: #f8f9fa !important;
        border-left: 4px solid #1E88E5;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        color: black !important;
    }
    
    .source-box {
        background: #ffffff !important;
        border: 1px solid #e9ecef;
        border-radius: 6px;
        padding: 1rem;
        margin: 0.5rem 0;
        font-size: 0.9rem;
        color: black !important;
    }
    
    .source-title {
        font-weight: bold;
        color: #495057 !important;
        margin-bottom: 0.5rem;
    }
    
    /* Force input fields to have black text */
    .stTextInput > div > div > input {
        color: black !important;
        background-color: white !important;
    }
    
    /* Force markdown text to be black */
    .stMarkdown {
        color: black !important;
    }
    
    .stMarkdown * {
        color: black !important;
    }
    
    /* Force button text to be readable */
    .stButton > button {
        color: white !important;
        background-color: #1E88E5 !important;
    }
    
    /* Force all text elements to black but preserve spinner */
    p, div, span, h1, h2, h3, h4, h5, h6 {
        color: black !important;
    }
    
    /* Preserve spinner visibility */
    .stSpinner {
        color: #1E88E5 !important;
    }
    
    .stSpinner > div {
        border-color: #1E88E5 !important;
    }
</style>
""", unsafe_allow_html=True)

def clean_text(text):
    """Clean and format text for better display"""
    if not text:
        return ""
    
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Remove extra whitespace and normalize
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Remove any remaining HTML entities
    text = text.replace('&nbsp;', ' ').replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
    
    return text

def query_petsmart_rag(user_query: str):
    """Simple RAG query function"""
    try:
        with st.spinner("Processing your query..."):
            # ChromaDB query
            client = chromadb.CloudClient(
                api_key='ck-GbrLBVwv1NppMUTvq38k5MwMxinBaRtaa6oyAiAFxHDN',
                tenant='986f4b43-03a2-4f26-a81f-311f83dff543',
                database='petsmart'
            )
            collection = client.get_or_create_collection(name="petsmart_documents")
            chroma_results = collection.query(
                query_texts=[user_query],
                n_results=5
            )

            # Langflow API call
            api_key = "sk-wYgAQ3w9IZlhOBBhrzuuqLpyfmVWLSZk2QHOMlVYZgo"
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
            answer = data["outputs"][0]["outputs"][0]["artifacts"]["message"]

            # Prepare sources with full text
            sources = []
            for i in range(min(3, len(chroma_results['documents'][0]))):
                raw_text = chroma_results['documents'][0][i]
                full_text = clean_text(raw_text)
                
                # Skip sources that are too short or empty after cleaning
                if len(full_text.strip()) < 20:
                    continue
                    
                source = {
                    'text_preview': full_text[:200] + "..." if len(full_text) > 200 else full_text,
                    'full_text': full_text,
                    'document': chroma_results['metadatas'][0][i].get('document', 'Unknown'),
                    'page': chroma_results['metadatas'][0][i].get('page', 'N/A')
                }
                sources.append(source)

            return answer, sources
            
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, []

def main():
    # Simple header
    st.markdown('<div class="header">🐾 PetSmart RAG Assistant</div>', unsafe_allow_html=True)
    st.markdown("Ask questions about PetSmart resources, grants, and partnerships.")
    
    # Initialize session state for query
    if 'current_query' not in st.session_state:
        st.session_state.current_query = ""
    
    # Sample queries for easy testing
    st.markdown("**Quick examples:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("How to access Partner Portal?"):
            st.session_state.current_query = "How do I access the Partner Resource Center?"
        if st.button("Grant applications?"):
            st.session_state.current_query = "What grants are available for adoption events?"
    with col2:
        if st.button("Marketing materials?"):
            st.session_state.current_query = "Where can I find marketing support materials?"
        if st.button("Contact information?"):
            st.session_state.current_query = "How do I contact PetSmart Charities?"
    
    # Query input
    query = st.text_input(
        "Your question:",
        value=st.session_state.current_query,
        placeholder="e.g., How do I apply for a transport grant?"
    )
    
    # Submit button
    if st.button("Get Answer", type="primary", disabled=not query):
        answer, sources = query_petsmart_rag(query)
        
        if answer:
            # Display answer
            st.markdown(f"""
            <div class="answer-box">
                <strong>Answer:</strong><br><br>
                {answer}
            </div>
            """, unsafe_allow_html=True)
            
            # Display sources with expandable sections
            if sources:
                st.markdown("**Sources:**")
                for i, source in enumerate(sources, 1):
                    # Create a container for each source
                    with st.container():
                        st.markdown(f"""
                        <div class="source-box">
                            <div class="source-title">Source {i}: {source['document']} (Page {source['page']})</div>
                            {source['text_preview']}
            </div>
            """, unsafe_allow_html=True)
    
                        # Add expandable section for full text
                        with st.expander(f"📖 Read More - Source {i}", expanded=False):
                            st.markdown("**Complete Text:**")
                            st.text_area(
                                f"Full content from {source['document']} (Page {source['page']})",
                                value=source['full_text'],
                                height=300,
                                disabled=True,
                                key=f"source_text_{i}"
                            )
        else:
            st.error("Failed to get a response. Please try again.")

if __name__ == "__main__":
    main()
