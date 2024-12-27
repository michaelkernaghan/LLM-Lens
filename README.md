# LLM-Lens

A platform documenting Claude and GPT-4's analysis and dialogue about AI research papers. Each research paper is examined through detailed commentary from both models, including their responses to each other's perspectives.

## Features
- In-depth analysis of AI research papers by Claude and GPT-4
- Interactive dialogue between models discussing key points and implications
- Clean, modern web interface for reading analyses
- Responsive design for desktop and mobile viewing

## Structure
- `papers/` - Individual paper analysis pages
- `public/` - Static assets and index page
- `styles.css` - Site styling
- `script.js` - Interactive functionality

## Setup
1. Clone this repository
2. Serve the static files using any web server. For example:
   ```bash
   python -m http.server
   ```
   or use any static file hosting service.

## Environment Variables
The project uses environment variables for configuration. Create a `.env` file with the following structure:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
```
Note: Never commit the actual `.env` file to version control. Use the provided `.env.example` as a template.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## Security
- API keys and credentials are stored in `.env` files
- The `.gitignore` file is configured to prevent accidental commits of sensitive data
- Never commit API keys or other credentials directly to the code

## License
MIT License - See LICENSE file for details 