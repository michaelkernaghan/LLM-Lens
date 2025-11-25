import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# DALL-E prompt
prompt = """A modern tech conference poster design showcasing 'Building AI Agents with the Eliza Framework: A Case Study of LLMLens'. The central image features an elegant visualization of interconnected nodes representing the Eliza framework, with a prominent lens/prism element transforming code fragments into intelligent agents. Multiple smaller AI agents emerge from the framework, with LLMLens highlighted as the primary example. Clean, minimalist design with a white background and subtle tech grid patterns. The visualization uses professional typography and shows flowing data streams in cool blues and purples, with occasional bright accent colors. Key framework components are labeled with elegant typography. The overall aesthetic balances technical sophistication with academic professionalism, suitable for a developer conference or tech talk. Include subtle visual elements representing Twitter integration and critical analysis capabilities."""

try:
    # Generate image
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="hd",
        n=1,
    )

    # Get the URL of the generated image
    image_url = response.data[0].url
    print(f"Image generated successfully!")
    print(f"Image URL: {image_url}")

except Exception as e:
    print(f"An error occurred: {str(e)}")