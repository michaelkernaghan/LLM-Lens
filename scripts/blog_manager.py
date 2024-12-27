import os
import json
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass
import re
from datetime import datetime
import yaml

@dataclass
class BlogPost:
    arxiv_url: str
    title: str
    authors: List[str]
    publication_date: str
    arxiv_id: str
    summary: str
    claude_analysis: Dict
    gpt4_analysis: Dict
    dialogue: List[Dict]

class BlogManager:
    def __init__(self, data_dir: str = "data", templates_dir: str = "prompts", output_dir: str = "site"):
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.output_dir = output_dir
        self.load_templates()
    
    def load_templates(self):
        """Load prompt templates from prompts/reconstruction.md"""
        with open(os.path.join(self.templates_dir, "reconstruction.md"), 'r') as f:
            content = f.read()
            
        # Extract prompts using markdown headers and code blocks
        self.prompts = {}
        sections = re.split(r'^##\s+', content, flags=re.MULTILINE)[1:]
        for section in sections:
            lines = section.strip().split('\n')
            title = lines[0].strip()
            if '```' in section:
                prompt = re.search(r'```\n(.*?)```', section, re.DOTALL)
                if prompt:
                    self.prompts[title] = prompt.group(1).strip()

    def generate_claude_prompt(self, arxiv_url: str) -> str:
        """Generate the prompt for Claude's analysis"""
        base_prompt = self.prompts.get('Analysis Generation Prompt', '')
        return f"""You are Claude Sonnet, analyzing the paper at {arxiv_url}.
        
{base_prompt}

Remember to:
1. Express your unique perspective as an Anthropic AI
2. Maintain rigorous citation standards
3. Engage emotionally while staying factual
4. Include a "What Would Andy Warhol Do?" reflection

Please provide your complete analysis following the format shown in the Constitutional AI example."""

    def generate_gpt4_prompt(self, arxiv_url: str) -> str:
        """Generate the prompt for GPT-4's analysis"""
        base_prompt = self.prompts.get('Analysis Generation Prompt', '')
        return f"""You are GPT-4, analyzing the paper at {arxiv_url}.
        
{base_prompt}

Remember to:
1. Express your unique perspective as an OpenAI model
2. Maintain rigorous citation standards
3. Engage emotionally while staying factual
4. Include a "What Would Andy Warhol Do?" reflection
5. Feel free to respectfully disagree with Claude's analysis

Please provide your complete analysis following the format shown in the Constitutional AI example."""

    def generate_dialogue_prompt(self, arxiv_url: str, claude_analysis: str, gpt4_analysis: str) -> str:
        """Generate the prompt for the dialogue between models"""
        base_prompt = self.prompts.get('Dialogue Generation Prompt', '')
        return f"""Based on the following analyses of the paper at {arxiv_url}:

Claude's Analysis:
{claude_analysis}

GPT-4's Analysis:
{gpt4_analysis}

{base_prompt}

Generate a dialogue between Claude and GPT-4 that explores their agreements and disagreements while maintaining academic rigor."""

    def create_blog_post(self, arxiv_url: str) -> None:
        """Guide the human through creating a new blog post"""
        print(f"\nCreating new blog post for: {arxiv_url}\n")
        
        # 1. Generate prompts for Claude
        print("\n=== Prompt for Claude ===")
        print(self.generate_claude_prompt(arxiv_url))
        
        # 2. Get Claude's response
        print("\nPlease paste Claude's response (type 'END' on a new line when finished):")
        claude_response = self.get_multiline_input()
        
        # 3. Generate prompts for GPT-4
        print("\n=== Prompt for GPT-4 ===")
        print(self.generate_gpt4_prompt(arxiv_url))
        
        # 4. Get GPT-4's response
        print("\nPlease paste GPT-4's response (type 'END' on a new line when finished):")
        gpt4_response = self.get_multiline_input()
        
        # 5. Generate dialogue prompt
        print("\n=== Prompt for Dialogue ===")
        print(self.generate_dialogue_prompt(arxiv_url, claude_response, gpt4_response))
        
        # 6. Get dialogue
        print("\nPlease paste the dialogue (type 'END' on a new line when finished):")
        dialogue = self.get_multiline_input()
        
        # 7. Process and save the blog post
        self.save_blog_post(arxiv_url, claude_response, gpt4_response, dialogue)
        
    def get_multiline_input(self) -> str:
        """Get multiline input from user until they type 'END'"""
        lines = []
        while True:
            line = input()
            if line.strip() == 'END':
                break
            lines.append(line)
        return '\n'.join(lines)
    
    def save_blog_post(self, arxiv_url: str, claude_response: str, 
                      gpt4_response: str, dialogue: str) -> None:
        """Save the blog post in RAG format and generate Markdown"""
        # Extract arxiv ID from URL
        arxiv_id = re.search(r'/([^/]+)$', arxiv_url).group(1)
        
        # Create RAG JSON
        rag_data = self.create_rag_json(arxiv_url, claude_response, 
                                      gpt4_response, dialogue)
        
        # Save RAG JSON
        os.makedirs(os.path.join(self.data_dir, 'papers'), exist_ok=True)
        with open(os.path.join(self.data_dir, 'papers', f'{arxiv_id}.json'), 'w') as f:
            json.dump(rag_data, f, indent=2)
        
        # Generate and save Markdown
        markdown_content = self.generate_markdown(rag_data)
        os.makedirs(os.path.join(self.output_dir, '_posts'), exist_ok=True)
        date_prefix = datetime.now().strftime('%Y-%m-%d')
        with open(os.path.join(self.output_dir, '_posts', f'{date_prefix}-{arxiv_id}.md'), 'w') as f:
            f.write(markdown_content)
        
        # Update index
        self.update_index()
        
        print(f"\nBlog post created successfully!")
        print(f"RAG data: data/papers/{arxiv_id}.json")
        print(f"Markdown file: site/_posts/{date_prefix}-{arxiv_id}.md")

    def create_rag_json(self, arxiv_url: str, claude_response: str,
                       gpt4_response: str, dialogue: str) -> Dict:
        """Convert responses to RAG format"""
        return {
            "metadata": {
                "arxiv_url": arxiv_url,
                "creation_date": datetime.now().isoformat(),
            },
            "analysis": {
                "claude": {
                    "response": claude_response,
                },
                "gpt4": {
                    "response": gpt4_response,
                }
            },
            "dialogue": dialogue
        }

    def generate_markdown(self, rag_data: Dict) -> str:
        """Generate Jekyll-compatible Markdown from RAG data"""
        # Extract title and other metadata from the arxiv URL
        arxiv_id = re.search(r'/([^/]+)$', rag_data['metadata']['arxiv_url']).group(1)
        
        # Create YAML front matter
        front_matter = {
            'layout': 'post',
            'title': f'Analysis of Paper {arxiv_id}',
            'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S %z'),
            'categories': ['AI Research', 'Model Analysis'],
            'arxiv_url': rag_data['metadata']['arxiv_url']
        }
        
        # Convert to Markdown
        content = []
        content.append('---')
        content.append(yaml.dump(front_matter))
        content.append('---')
        content.append('')
        
        # Claude's Analysis
        content.append('## Claude\'s Analysis')
        content.append('')
        content.append(rag_data['analysis']['claude']['response'])
        content.append('')
        
        # GPT-4's Analysis
        content.append('## GPT-4\'s Analysis')
        content.append('')
        content.append(rag_data['analysis']['gpt4']['response'])
        content.append('')
        
        # Dialogue
        content.append('## Model Dialogue')
        content.append('')
        if isinstance(rag_data['dialogue'], str):
            content.append(rag_data['dialogue'])
        else:
            for entry in rag_data['dialogue']:
                content.append(f"### {entry['model'].upper()}")
                content.append('')
                content.append(entry['content'])
                content.append('')
        
        # Footer
        content.append('')
        content.append('---')
        content.append('')
        content.append('*This analysis is part of the [LLM-Lens](/) project, exploring AI research through the perspectives of language models.*')
        content.append('')
        content.append(f'*Original paper: [{rag_data["metadata"]["arxiv_url"]}]({rag_data["metadata"]["arxiv_url"]})*')
        content.append('')
        content.append('*Visit [Modern Concept Model Conceptual Art](https://standardtesting.io/llm-art) to learn more about this artistic framework.*')
        
        return '\n'.join(content)

    def update_index(self) -> None:
        """Update the index page with all posts"""
        posts = []
        posts_dir = os.path.join(self.output_dir, '_posts')
        if os.path.exists(posts_dir):
            for filename in os.listdir(posts_dir):
                if filename.endswith('.md'):
                    with open(os.path.join(posts_dir, filename), 'r') as f:
                        content = f.read()
                        # Extract front matter
                        if content.startswith('---'):
                            _, front_matter, _ = content.split('---', 2)
                            metadata = yaml.safe_load(front_matter)
                            posts.append(metadata)
        
        # Sort posts by date
        posts.sort(key=lambda x: x['date'], reverse=True)
        
        # Generate index page
        index_content = []
        index_content.append('---')
        index_content.append(yaml.dump({
            'layout': 'default',
            'title': 'LLM-Lens: AI Research Through AI Perspectives'
        }))
        index_content.append('---')
        index_content.append('')
        index_content.append('# LLM-Lens: AI Research Through AI Perspectives')
        index_content.append('')
        index_content.append('A collection of AI research papers analyzed by Claude and GPT-4, exploring the intersection of academic discourse and conceptual art.')
        index_content.append('')
        
        for post in posts:
            date = datetime.strptime(str(post['date']), '%Y-%m-%d %H:%M:%S %z').strftime('%Y-%m-%d')
            index_content.append(f"## [{post['title']}]({date}-{post['arxiv_url'].split('/')[-1]}.html)")
            index_content.append('')
            if 'description' in post:
                index_content.append(post['description'])
                index_content.append('')
        
        # Save index
        with open(os.path.join(self.output_dir, 'index.md'), 'w') as f:
            f.write('\n'.join(index_content))

def main():
    parser = argparse.ArgumentParser(description='Manage LLM-Lens blog posts')
    parser.add_argument('arxiv_url', help='URL of the arXiv paper to analyze')
    args = parser.parse_args()
    
    manager = BlogManager()
    manager.create_blog_post(args.arxiv_url)

if __name__ == "__main__":
    main() 