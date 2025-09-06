# Langflow API Response Format

## Expected Data Structure

Our PetSmart RAG Assistant expects a specific JSON structure from the Langflow API. Here's the detailed format:

## 🎯 Core Response Structure

```json
{
  "answer": "string",
  "chunks": [
    {
      "text": "string",
      "metadata": {
        "page": "number",
        "document": "string", 
        "snippet": "string",
        "pdf_path": "string",
        "links_count": "number",
        "links_json": "string (JSON array as string)"
      },
      "similarity": "number (0.0 to 1.0)"
    }
  ]
}
```

## 📋 Detailed Field Requirements

### Required Fields:
- **`answer`** (string): The main RAG-generated response text
- **`chunks`** (array): Array of source document chunks used to generate the answer

### Chunk Fields:
- **`text`** (string): The actual text content from the document
- **`similarity`** (number): Similarity score between 0.0 and 1.0
- **`metadata`** (object): Metadata about the source document

### Metadata Fields:
- **`document`** (string): Name of the source document (e.g., "PetSmart Guide", "PetSmart Manual")
- **`page`** (number): Page number in the source document
- **`pdf_path`** (string): Path to the source PDF file
- **`snippet`** (string): Short preview of the text (first ~50 characters)
- **`links_count`** (number): Number of links found in this chunk
- **`links_json`** (string): JSON string containing extracted links array

## 🔗 Links JSON Format

The `links_json` field should contain a stringified JSON array:

```json
"[{\"text\": \"Partner Resource Center\", \"url\": \"https://petsmartcharities.org/pro/resources\"}, {\"text\": \"Contact Email\", \"url\": \"mailto:support@petsmartcharities.org\"}]"
```

## 📊 Complete Example

```json
{
  "answer": "To access marketing support materials, you can visit the Partner Resource Center. The US version is available at https://petsmartcharities.org/pro/resources and the Canadian version at https://petsmartcharities.ca/pro/resources. You'll find grant recipient toolkits, brand guidelines, and official logos for both US and Canadian partners.",
  "chunks": [
    {
      "text": "Partner Resource Center US [https://petsmartcharities.org/pro/resources] • Partner Resource Centre Canada [https://petsmartcharities.ca/pro/resources] Marketing Support Links Grant Recipient Toolkit: Use these tools to spread the word about our partnership!",
      "metadata": {
        "page": 2,
        "document": "PetSmart Guide",
        "snippet": "Partner Resource Center US [https://petsmartchari",
        "pdf_path": "petsmart_guide.pdf",
        "links_count": 2,
        "links_json": "[{\"text\": \"Partner Resource Center US\", \"url\": \"https://petsmartcharities.org/pro/resources\"}, {\"text\": \"Partner Resource Centre Canada\", \"url\": \"https://petsmartcharities.ca/pro/resources\"}]"
      },
      "similarity": 0.892
    },
    {
      "text": "US Grant Recipient Toolkit [https://petsmartcharities.org/pro/resources/marketing-support/grant-recipient-toolkit-us] Canadian Grant Recipient Toolkit [https://petsmartcharities.ca/pro/resources/marketing-support/grant-recipient-toolkit-ca]",
      "metadata": {
        "page": 3,
        "document": "PetSmart Guide",
        "snippet": "US Grant Recipient Toolkit [https://petsmartcha",
        "pdf_path": "petsmart_guide.pdf",
        "links_count": 2,
        "links_json": "[{\"text\": \"US Grant Recipient Toolkit\", \"url\": \"https://petsmartcharities.org/pro/resources/marketing-support/grant-recipient-toolkit-us\"}, {\"text\": \"Canadian Grant Recipient Toolkit\", \"url\": \"https://petsmartcharities.ca/pro/resources/marketing-support/grant-recipient-toolkit-ca\"}]"
      },
      "similarity": 0.856
    }
  ]
}
```

## 🔧 Flexibility and Adaptations

### What's Flexible:
- **Additional fields**: You can add extra fields to chunks or metadata - they'll be ignored
- **Field order**: JSON field order doesn't matter
- **Empty arrays**: `chunks` can be empty (though not recommended)
- **Missing optional metadata**: Some metadata fields can be missing (defaults will be used)

### What's Required:
- **Core structure**: Must have `answer` and `chunks` at root level
- **Chunk essentials**: Each chunk must have `text` and `similarity`
- **Data types**: Must match expected types (strings, numbers, objects)

### Default Values Used:
- Missing `document`: "Unknown"
- Missing `page`: "?"
- Missing `similarity`: 0.0
- Missing `links_count`: 0
- Missing `links_json`: "[]"

## 🚨 Common Issues to Avoid:

1. **String vs Number**: Ensure `similarity` is a number, not a string
2. **JSON Escaping**: Properly escape quotes in `links_json` string
3. **Empty Values**: Provide meaningful defaults rather than null/undefined
4. **Array Structure**: `chunks` must be an array, even if empty

## 🛠️ Testing Your API

You can test your Langflow API response format using our demo app with the sample data, or validate against this structure before connecting to the production interface.
