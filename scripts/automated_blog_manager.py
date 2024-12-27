import os
import json
import argparse
from typing import Dict, List, Optional
from dataclasses import dataclass
import re
from datetime import datetime
import anthropic
import openai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AutomatedBlogManager:
    def __init__(self, data_dir: str = "data", templates_dir: str = "prompts"):
        self.data_dir = data_dir
        self.templates_dir = templates_dir
        self.load_templates()
        
        # Initialize API clients
        self.claude = anthropic.Client(os.getenv("ANTHROPIC_API_KEY"))
        openai.api_key = os.getenv("OPENAI_API_KEY")
    
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

    def get_claude_analysis(self, arxiv_url: str) -> str:
        """Get analysis from Claude via API"""
        prompt = self.generate_claude_prompt(arxiv_url)
        
        response = self.claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            temperature=0.7,
            system="You are Claude Sonnet, an AI assistant focused on analyzing AI research papers with both academic rigor and emotional engagement.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text

    def get_gpt4_analysis(self, arxiv_url: str, claude_analysis: str) -> str:
        """Get analysis from GPT-4 via API"""
        prompt = self.generate_gpt4_prompt(arxiv_url)
        
        response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are GPT-4, an AI assistant focused on analyzing AI research papers with both academic rigor and emotional engagement."},
                {"role": "user", "content": f"Claude's analysis:\n{claude_analysis}\n\n{prompt}"}
            ]
        )
        
        return response.choices[0].message.content

    def get_dialogue(self, arxiv_url: str, claude_analysis: str, gpt4_analysis: str) -> str:
        """Generate dialogue via alternating API calls"""
        dialogue = []
        prompt = self.generate_dialogue_prompt(arxiv_url, claude_analysis, gpt4_analysis)
        
        # Start with Claude
        claude_response = self.claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            system="You are Claude Sonnet engaging in a dialogue about an AI research paper. Respond as Claude, maintaining academic rigor while expressing genuine perspectives.",
            messages=[{"role": "user", "content": prompt}]
        )
        dialogue.append({"model": "claude", "content": claude_response.content[0].text})
        
        # GPT-4 response
        gpt4_response = openai.ChatCompletion.create(
            model="gpt-4-turbo-preview",
            temperature=0.7,
            messages=[
                {"role": "system", "content": "You are GPT-4 engaging in a dialogue about an AI research paper. Respond as GPT-4, maintaining academic rigor while expressing genuine perspectives."},
                {"role": "user", "content": f"{prompt}\n\nClaude's response:\n{claude_response.content[0].text}"}
            ]
        )
        dialogue.append({"model": "gpt4", "content": gpt4_response.choices[0].message.content})
        
        # Final Claude response
        final_claude = self.claude.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            temperature=0.7,
            system="You are Claude Sonnet engaging in a dialogue about an AI research paper. This is your final response in the dialogue.",
            messages=[{"role": "user", "content": f"{prompt}\n\nDialogue so far:\n{json.dumps(dialogue, indent=2)}"}]
        )
        dialogue.append({"model": "claude", "content": final_claude.content[0].text})
        
        return dialogue

    def create_blog_post(self, arxiv_url: str) -> None:
        """Create a blog post using API calls"""
        print(f"\nCreating new blog post for: {arxiv_url}\n")
        
        # 1. Get Claude's analysis
        print("Getting Claude's analysis...")
        claude_analysis = self.get_claude_analysis(arxiv_url)
        
        # 2. Get GPT-4's analysis
        print("Getting GPT-4's analysis...")
        gpt4_analysis = self.get_gpt4_analysis(arxiv_url, claude_analysis)
        
        # 3. Generate dialogue
        print("Generating dialogue...")
        dialogue = self.get_dialogue(arxiv_url, claude_analysis, gpt4_analysis)
        
        # 4. Save the blog post
        self.save_blog_post(arxiv_url, claude_analysis, gpt4_analysis, dialogue)
    
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

    def save_blog_post(self, arxiv_url: str, claude_analysis: str, 
                      gpt4_analysis: str, dialogue: List[Dict]) -> None:
        """Save the blog post in RAG format and generate HTML"""
        # Extract arxiv ID from URL
        arxiv_id = re.search(r'/([^/]+)$', arxiv_url).group(1)
        
        # Create RAG JSON
        rag_data = self.create_rag_json(arxiv_url, claude_analysis, 
                                      gpt4_analysis, dialogue)
        
        # Save RAG JSON
        os.makedirs(os.path.join(self.data_dir, 'papers'), exist_ok=True)
        with open(os.path.join(self.data_dir, 'papers', f'{arxiv_id}.json'), 'w') as f:
            json.dump(rag_data, f, indent=2)
        
        # Generate and save HTML
        html_content = self.generate_html(rag_data)
        os.makedirs('papers', exist_ok=True)
        with open(f'papers/{arxiv_id}.html', 'w') as f:
            f.write(html_content)
        
        print(f"\nBlog post created successfully!")
        print(f"RAG data: data/papers/{arxiv_id}.json")
        print(f"HTML file: papers/{arxiv_id}.html")

    def create_rag_json(self, arxiv_url: str, claude_analysis: str,
                       gpt4_analysis: str, dialogue: List[Dict]) -> Dict:
        """Convert responses to RAG format"""
        return {
            "metadata": {
                "arxiv_url": arxiv_url,
                "creation_date": datetime.now().isoformat(),
            },
            "analysis": {
                "claude": {
                    "response": claude_analysis,
                },
                "gpt4": {
                    "response": gpt4_analysis,
                }
            },
            "dialogue": dialogue
        }

    def generate_html(self, rag_data: Dict) -> str:
        """Generate HTML from RAG data"""
        # This would use the existing HTML template from constitutional-ai.html
        # For now, return a basic structure
        return f"""<!DOCTYPE html>
<html>
<head><title>Analysis of {rag_data['metadata']['arxiv_url']}</title></head>
<body>
    <!-- Add proper HTML structure -->
</body>
</html>"""

def main():
    parser = argparse.ArgumentParser(description='Automated LLM-Lens blog post creation')
    parser.add_argument('arxiv_url', help='URL of the arXiv paper to analyze')
    args = parser.parse_args()
    
    manager = AutomatedBlogManager()
    manager.create_blog_post(args.arxiv_url)

if __name__ == "__main__":
    main() 