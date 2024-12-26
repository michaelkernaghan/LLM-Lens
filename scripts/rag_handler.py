import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
import numpy as np
from datetime import datetime

@dataclass
class PaperMetadata:
    title: str
    authors: List[str]
    publication_date: str
    arxiv_id: Optional[str] = None
    paper_url: Optional[str] = None
    tags: List[str] = None

@dataclass
class PaperContent:
    summary: str
    key_points: Optional[List[str]] = None
    methodology: Optional[str] = None
    results: Optional[str] = None
    implications: Optional[str] = None

@dataclass
class ModelAnalysis:
    version: str
    main_analysis: str
    key_insights: List[str]
    concerns: List[str]
    related_papers: List[Dict[str, str]]

@dataclass
class DialogueEntry:
    model: str
    content: str
    references: List[Dict[str, str]]

class RAGPaperHandler:
    def __init__(self, data_dir: str = "data/papers"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def load_paper(self, paper_id: str) -> Dict:
        """Load a paper's RAG data from JSON."""
        file_path = os.path.join(self.data_dir, f"{paper_id}.json")
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise ValueError(f"Paper {paper_id} not found")

    def save_paper(self, paper_id: str, data: Dict) -> None:
        """Save a paper's RAG data to JSON."""
        file_path = os.path.join(self.data_dir, f"{paper_id}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)

    def list_papers(self) -> List[Dict]:
        """List all available papers with their basic metadata."""
        papers = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith('.json'):
                paper_data = self.load_paper(filename[:-5])
                papers.append({
                    'id': filename[:-5],
                    'metadata': paper_data['metadata']
                })
        return sorted(papers, key=lambda x: x['metadata']['publication_date'], reverse=True)

    def search_papers(self, query: str, fields: List[str] = None) -> List[Dict]:
        """Search papers based on a text query."""
        # In a real implementation, this would use embeddings and vector similarity
        # For now, we'll do simple text matching
        results = []
        for paper in self.list_papers():
            paper_data = self.load_paper(paper['id'])
            score = self._calculate_relevance(paper_data, query, fields)
            if score > 0:
                results.append({
                    'id': paper['id'],
                    'metadata': paper_data['metadata'],
                    'relevance_score': score
                })
        return sorted(results, key=lambda x: x['relevance_score'], reverse=True)

    def _calculate_relevance(self, paper_data: Dict, query: str, fields: List[str] = None) -> float:
        """Calculate relevance score for a paper against a query."""
        if fields is None:
            fields = ['metadata.title', 'content.summary', 'analysis.*.main_analysis']
        
        score = 0
        query = query.lower()
        
        for field in fields:
            if field == 'metadata.title':
                if query in paper_data['metadata']['title'].lower():
                    score += 2
            elif field == 'content.summary':
                if query in paper_data['content']['summary'].lower():
                    score += 1
            elif field == 'analysis.*.main_analysis':
                for model in ['claude', 'gpt4']:
                    if model in paper_data['analysis']:
                        if query in paper_data['analysis'][model]['main_analysis'].lower():
                            score += 0.5
        
        return score

    def get_related_papers(self, paper_id: str) -> List[str]:
        """Get papers related to a given paper based on model analyses."""
        paper_data = self.load_paper(paper_id)
        related = set()
        
        for model in ['claude', 'gpt4']:
            if model in paper_data['analysis']:
                for ref in paper_data['analysis'][model].get('related_papers', []):
                    related.add(ref['title'])
        
        return list(related)

    def get_model_dialogue(self, paper_id: str) -> List[DialogueEntry]:
        """Get the model dialogue for a paper."""
        paper_data = self.load_paper(paper_id)
        return [DialogueEntry(**entry) for entry in paper_data.get('dialogue', [])]

    def add_dialogue_entry(self, paper_id: str, model: str, content: str, 
                         references: List[Dict[str, str]]) -> None:
        """Add a new dialogue entry to a paper."""
        paper_data = self.load_paper(paper_id)
        if 'dialogue' not in paper_data:
            paper_data['dialogue'] = []
        
        paper_data['dialogue'].append({
            'model': model,
            'content': content,
            'references': references
        })
        
        self.save_paper(paper_id, paper_data)

# Example usage:
if __name__ == "__main__":
    handler = RAGPaperHandler()
    
    # List all papers
    papers = handler.list_papers()
    print(f"Found {len(papers)} papers")
    
    # Search papers
    results = handler.search_papers("ethical constraints")
    print(f"Found {len(results)} relevant papers")
    
    # Get related papers
    if papers:
        related = handler.get_related_papers(papers[0]['id'])
        print(f"Found {len(related)} related papers") 