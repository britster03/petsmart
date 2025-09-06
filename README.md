# 🐾 PetSmart RAG Assistant

An impressive Streamlit interface for displaying RAG (Retrieval-Augmented Generation) responses from Langflow APIs, featuring interactive knowledge graph visualization and comprehensive link extraction.

## ✨ Features

### 🎯 **Smart RAG Interface**
- Beautiful, responsive Streamlit UI with custom styling
- Real-time API integration with Langflow
- Comprehensive response analysis and metrics

### 🕸️ **Interactive Knowledge Graph**
- Visual representation of query-answer-source relationships using [streamlit-agraph](https://github.com/ChrisDelClea/streamlit-agraph)
- Color-coded nodes for different document types
- Clickable nodes for detailed exploration
- Link relationships showing document connections

### 🔗 **Advanced Link Extraction**
- Automatic extraction of all embedded hyperlinks from source documents
- Support for HTTP/HTTPS URLs and email addresses
- Categorized link display (Resource Centers, Grants, Social Media, etc.)
- Domain-grouped link organization

### 📊 **Rich Analytics**
- Source document distribution charts
- Similarity score visualization
- Chunk metadata analysis
- Performance metrics

## 🚀 Quick Start

### Installation

1. **Clone and navigate to the project:**
```bash
cd /path/to/petsmart
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

### Demo Mode

**Try the demo first to see the interface:**
```bash
streamlit run demo_app.py
```

This will show you exactly how the interface works with sample data.

### Production Mode

**For real Langflow integration:**
```bash
streamlit run streamlit_app.py
```

## 🔧 Configuration

### Langflow API Integration

1. **Enter your Langflow API URL** in the sidebar
2. **Ensure your Langflow returns data in this format:**

```json
{
  "answer": "Your generated answer text",
  "chunks": [
    {
      "text": "Source text with embedded URLs [https://example.com]",
      "metadata": {
        "page": 1,
        "document": "Document Name",
        "snippet": "Preview text...",
        "pdf_path": "document.pdf",
        "links_count": 5,
        "links_json": "[{\"text\": \"Link Text\", \"url\": \"https://example.com\"}]"
      },
      "similarity": 0.95
    }
  ]
}
```

### Customization Options

**Graph Settings:**
- Physics simulation toggle
- Hierarchical vs. force-directed layout
- Adjustable graph dimensions

**Display Options:**
- Metadata visibility control
- Link extraction toggle
- Maximum chunks to display

## 📁 Project Structure

```
petsmart/
├── streamlit_app.py          # Main production app
├── demo_app.py              # Demo version with sample data
├── embeddings.py            # Enhanced PDF ingestion with link extraction
├── test_enhanced_rag.py     # RAG system testing
├── requirements.txt         # Python dependencies
├── sample_response.json     # Sample API response format
└── README.md               # This file
```

## 🎨 Interface Highlights

### Main Dashboard
- **Query Input**: Clean, intuitive search interface
- **Sample Queries**: Pre-built example questions
- **Real-time Processing**: Live API call status

### Response Display
- **Structured Answer**: Highlighted main response
- **Metrics Cards**: Key statistics at a glance
- **Knowledge Graph**: Interactive visual representation
- **Source Chunks**: Expandable detail panels

### Link Management
- **Automatic Extraction**: Finds all URLs in source text
- **Smart Categorization**: Groups links by type and domain
- **Click-to-Open**: Direct navigation to external resources
- **Visual Indicators**: Color-coded link types

## 🔍 Knowledge Graph Features

### Node Types
- **🔵 Query Node**: Central user question (blue)
- **🟢 Answer Node**: Generated response (green)
- **🟠 Guide Chunks**: PetSmart Guide sources (orange)
- **🟣 Manual Chunks**: PetSmart Manual sources (purple)
- **🔺 Link Nodes**: External resources (pink triangles)

### Interactive Elements
- **Click nodes** to see details
- **Hover effects** for better UX
- **Physics simulation** for natural layout
- **Zoom and pan** capabilities

## 🛠️ Advanced Usage

### Custom API Payloads

Modify the `call_langflow_api()` function to match your specific Langflow setup:

```python
def call_langflow_api(self, query: str) -> Dict[str, Any]:
    payload = {
        "query": query,
        "stream": False,
        # Add your custom parameters here
        "max_chunks": 5,
        "similarity_threshold": 0.7
    }
    # ... rest of the function
```

### Styling Customization

Update the CSS in the `st.markdown()` sections to match your brand:

```python
st.markdown("""
<style>
    .main-header {
        color: #YOUR_BRAND_COLOR;
        /* Add your custom styles */
    }
</style>
""", unsafe_allow_html=True)
```

## 📊 Supported Link Types

The system automatically detects and categorizes:

- **🏢 Resource Centers**: Partner portals and resource hubs
- **💰 Grant Applications**: Funding and application portals
- **📱 Social Media**: Facebook, Instagram, Twitter, YouTube
- **📧 Contact Info**: Email addresses and contact forms
- **🛠️ Partner Tools**: Lookup tools, manuals, and utilities
- **📄 Documents**: PDFs, guides, and documentation

## 🚨 Troubleshooting

### Common Issues

**API Connection Errors:**
- Verify your Langflow API URL is correct
- Check network connectivity
- Ensure API returns proper JSON format

**Graph Display Issues:**
- Try disabling physics simulation
- Reduce the number of chunks displayed
- Check browser console for JavaScript errors

**Link Extraction Problems:**
- Verify your PDF ingestion includes link extraction
- Check the `links_json` field in chunk metadata
- Ensure URLs are properly formatted in source text

## 🎯 Next Steps

1. **Connect to your Langflow API**
2. **Customize the styling** to match your brand
3. **Add additional visualizations** as needed
4. **Extend link categorization** for your specific use case


**Built with ❤️ for PetSmart Adoption Partners**

*Powered by Streamlit, streamlit-agraph, and Langflow*
