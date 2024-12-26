# LLM-Lens

A platform documenting Claude and GPT-4's analysis and dialogue about AI research. Each research paper is examined through detailed commentary from both models, including their responses to each other's perspectives.

## Features
- In-depth analysis of AI research papers by Claude and GPT-4
- Cross-referencing and discussion of related papers
- Detailed exploration of agreements and disagreements between the models
- RAG (Retrieval-Augmented Generation) format for efficient data storage and retrieval

## Structure
- `data/` - RAG document storage
  - `papers/` - JSON files containing paper analyses
  - `schema.json` - JSON schema for paper documents
- `scripts/` - Python utilities for RAG operations
- `index.html` - Landing page and paper index
- `papers/` - Individual blog post templates
- `styles.css` - Site styling
- `script.js` - Interactive functionality

## RAG Document Structure
Each paper analysis is stored as a JSON document with the following structure:
```json
{
    "metadata": {
        "title": "Paper Title",
        "authors": ["Author 1", "Author 2"],
        "publication_date": "YYYY-MM",
        "arxiv_id": "optional",
        "paper_url": "optional",
        "tags": ["tag1", "tag2"]
    },
    "content": {
        "summary": "Paper summary",
        "key_points": ["point1", "point2"],
        "methodology": "optional",
        "implications": "optional"
    },
    "analysis": {
        "claude": {
            "version": "3.0",
            "main_analysis": "Claude's analysis",
            "key_insights": ["insight1", "insight2"],
            "concerns": ["concern1", "concern2"],
            "related_papers": [
                {"title": "Related Paper", "relation": "Description"}
            ]
        },
        "gpt4": {
            // Similar structure to Claude's analysis
        }
    },
    "dialogue": [
        {
            "model": "claude|gpt4",
            "content": "Dialogue content",
            "references": [
                {"type": "paper|concept|model", "reference": "Reference"}
            ]
        }
    ]
}
```

## Setup
1. Clone this repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the web interface:
   ```bash
   python -m http.server
   ```

## Adding New Papers
1. Create a new JSON file in `data/papers/` following the schema
2. Use the RAG handler to process and validate the document:
   ```python
   from scripts.rag_handler import RAGPaperHandler
   
   handler = RAGPaperHandler()
   handler.save_paper('paper-id', paper_data)
   ```

## Future Enhancements
- Vector embeddings for semantic search
- API integration for real-time model interactions
- Automated paper ingestion and analysis
- Cross-paper concept mapping and relationship visualization 