# PetSmart AI Assistant - Modern Streamlit Interface
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
import datetime
import time
from htbuilder.units import rem
from htbuilder import div, styles

# Page configuration
st.set_page_config(
    page_title="PetSmart AI assistant", 
    page_icon="🐾",
    layout="centered"
)

# Configuration constants
MIN_TIME_BETWEEN_REQUESTS = datetime.timedelta(seconds=2)

# Comprehensive suggestion examples for PetSmart
SUGGESTIONS = {
    ":blue[:material/store:] Partner Portal Access": (
        "How do I access the Partner Resource Center and what resources are available?"
    ),
    ":green[:material/volunteer_activism:] Grant Applications": (
        "What grants are available for adoption events and how do I apply?"
    ),
    ":orange[:material/campaign:] Marketing Materials": (
        "Where can I find grant recipient toolkits, brand guidelines, and official logos?"
    ),
    ":violet[:material/contact_support:] Contact Information": (
        "How do I contact PetSmart Charities for marketing support and partnerships?"
    ),
    ":red[:material/pets:] Pet Transport Grants": (
        "How do I apply for a pet transport grant and what are the requirements?"
    ),
    ":yellow[:material/event:] Adoption Events": (
        "How do I organize an adoption event and what support does PetSmart provide?"
    ),
}

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
    """PetSmart RAG query function with modern UI feedback"""
    try:
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


def show_feedback_controls(message_index):
    """Shows the 'How did I do?' feedback control"""
    st.write("")
    
    with st.popover("How did I do?"):
        with st.form(key=f"feedback-{message_index}", border=False):
            with st.container(gap=None):
                st.markdown(":small[Rating]")
                rating = st.feedback(options="stars")
            
            details = st.text_area("More information (optional)")
            
            if st.checkbox("Include chat history with my feedback", True):
                relevant_history = st.session_state.messages[:message_index]
            else:
                relevant_history = []
            
            ""  # Add some space
            
            if st.form_submit_button("Send feedback"):
                st.success("Thank you for your feedback!")


@st.dialog("About PetSmart Assistant")
def show_disclaimer_dialog():
    st.markdown("""
    **PetSmart AI Assistant** is designed to help with questions about:
    
    - Partner Resource Center access
    - Grant applications and funding opportunities  
    - Marketing materials and promotional resources
    - Contact information for PetSmart Charities
    - Pet transport and adoption programs
    
    This assistant uses AI to search through PetSmart documentation and resources. 
    Answers may not always be complete or current. For official information, 
    please contact PetSmart Charities directly.
    """)

# -----------------------------------------------------------------------------
# Main UI Implementation

# Decorative header element
st.html(div(style=styles(font_size=rem(5), line_height=1))["🐾"])

title_row = st.container(
    horizontal=True,
    vertical_alignment="bottom",
)

with title_row:
    st.title(
        "PetSmart AI assistant",
        anchor=False,
        width="stretch",
    )

# Check for user interactions
user_just_asked_initial_question = (
    "initial_question" in st.session_state and st.session_state.initial_question
)

user_just_clicked_suggestion = (
    "selected_suggestion" in st.session_state and st.session_state.selected_suggestion
)

user_first_interaction = (
    user_just_asked_initial_question or user_just_clicked_suggestion
)

has_message_history = (
    "messages" in st.session_state and len(st.session_state.messages) > 0
)

# Show initial interface when no interaction yet
if not user_first_interaction and not has_message_history:
    st.session_state.messages = []
    
    with st.container():
        st.chat_input("Ask a question...", key="initial_question")
        
        selected_suggestion = st.pills(
            label="Examples",
            label_visibility="collapsed",
            options=SUGGESTIONS.keys(),
            key="selected_suggestion",
        )
    
    st.button(
        "&nbsp;:small[:gray[:material/info: About PetSmart Assistant]]",
        type="tertiary",
        on_click=show_disclaimer_dialog,
    )
    
    st.stop()

# Show chat input at the bottom when a question has been asked
user_message = st.chat_input("Ask a follow-up...")

if not user_message:
    if user_just_asked_initial_question:
        user_message = st.session_state.initial_question
    if user_just_clicked_suggestion:
        user_message = SUGGESTIONS[st.session_state.selected_suggestion]

with title_row:
    def clear_conversation():
        st.session_state.messages = []
        st.session_state.initial_question = None
        st.session_state.selected_suggestion = None
    
    st.button(
        "Restart",
        icon=":material/refresh:",
        on_click=clear_conversation,
    )

# Initialize rate limiting
if "prev_question_timestamp" not in st.session_state:
    st.session_state.prev_question_timestamp = datetime.datetime.fromtimestamp(0)

# Display chat messages from history as speech bubbles
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message["role"] == "assistant":
            st.container()  # Fix ghost message bug
        
        st.markdown(message["content"])
        
        if message["role"] == "assistant":
            show_feedback_controls(i)

if user_message:
    # When the user posts a message...
    
    # Display message as a speech bubble
    with st.chat_message("user"):
        st.text(user_message)
    
    # Display assistant response as a speech bubble
    with st.chat_message("assistant"):
        with st.spinner("Waiting..."):
            # Rate-limit if needed
            question_timestamp = datetime.datetime.now()
            time_diff = question_timestamp - st.session_state.prev_question_timestamp
            st.session_state.prev_question_timestamp = question_timestamp
            
            if time_diff < MIN_TIME_BETWEEN_REQUESTS:
                time.sleep(time_diff.total_seconds())
        
        # Research and get response
        with st.spinner("Researching..."):
            answer, sources = query_petsmart_rag(user_message)
        
        # Put everything after the spinners in a container to fix ghost message bug
        with st.container():
            if answer:
                # Stream the response
                st.markdown(answer)
                
                # Show sources as expandable sections
                if sources:
                    st.markdown("**📚 Sources:**")
                    for i, source in enumerate(sources, 1):
                        with st.expander(f"📄 {source['document']} (Page {source['page']})", expanded=False):
                            st.markdown(f"**Preview:** {source['text_preview']}")
                            st.markdown("**Full Content:**")
                            st.text_area(
                                "Source content",
                                value=source['full_text'],
                                height=200,
                                disabled=True,
                                key=f"source_{i}_{len(st.session_state.messages)}",
                                label_visibility="collapsed"
                            )
                
                # Add messages to chat history
                st.session_state.messages.append({"role": "user", "content": user_message})
                st.session_state.messages.append({"role": "assistant", "content": answer})
                
                # Show feedback controls
                show_feedback_controls(len(st.session_state.messages) - 1)
            else:
                error_message = "I apologize, but I encountered an issue while processing your question. Please try again or rephrase your question."
                st.markdown(error_message)
                
                # Add messages to chat history even for errors
                st.session_state.messages.append({"role": "user", "content": user_message})
                st.session_state.messages.append({"role": "assistant", "content": error_message})
