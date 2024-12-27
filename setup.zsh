#!/usr/bin/env zsh

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

# Run setup script
echo "Running setup script..."
python3 setup.py

echo "\nSetup complete! To create a new post:"
echo "1. Make sure you're in the virtual environment:"
echo "   source venv/bin/activate"
echo "\n2. Run the post creation script:"
echo "   python3 scripts/prepare_post.py https://arxiv.org/html/paper-id" 