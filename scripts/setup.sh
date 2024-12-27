#!/bin/bash

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Add local bin to PATH
export PATH="$HOME/.local/bin:$PATH"

# Create necessary directories
mkdir -p data/papers site/_posts site/_layouts site/_includes

# Create .env file if it doesn't exist
if [ ! -f "prompts/.env" ]; then
    echo "Creating .env file..."
    echo "ANTHROPIC_API_KEY=your_key_here" > prompts/.env
    echo "OPENAI_API_KEY=your_key_here" >> prompts/.env
fi

# Add PATH to .bashrc if not already present
if ! grep -q "export PATH=\"\$HOME/.local/bin:\$PATH\"" ~/.bashrc; then
    echo "Adding ~/.local/bin to PATH in .bashrc..."
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
fi

# Check if Jekyll is installed
if ! command -v jekyll &> /dev/null; then
    echo "Installing Jekyll..."
    gem install bundler jekyll
fi

# Create Gemfile if it doesn't exist
if [ ! -f "site/Gemfile" ]; then
    echo "Creating Gemfile..."
    cd site
    cat > Gemfile << EOL
source "https://rubygems.org"

gem "jekyll", "~> 4.2.0"
gem "minima", "~> 2.5"
gem "webrick", "~> 1.7"

group :jekyll_plugins do
  gem "jekyll-feed", "~> 0.12"
  gem "jekyll-seo-tag", "~> 2.6"
end
EOL
    cd ..
fi

# Install Jekyll dependencies
echo "Installing Jekyll dependencies..."
cd site
bundle install
cd ..

echo "Setup complete! To start developing:"
echo "1. source ~/.bashrc  # To update PATH"
echo "2. source venv/bin/activate  # To activate virtual environment"
echo "3. cd site && bundle exec jekyll serve  # To start local server"
echo ""
echo "To create a new blog post:"
echo "python scripts/blog_manager.py https://arxiv.org/html/paper-id" 