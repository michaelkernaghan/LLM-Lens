import os
import shutil

def setup():
    """Set up the project structure"""
    # Create directories
    os.makedirs('public/papers', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    # Copy templates if they don't exist
    if not os.path.exists('public/styles.css'):
        shutil.copy('styles.css', 'public/styles.css')
    
    # Copy template files
    for template in ['index.html', 'about.html']:
        if not os.path.exists(f'public/{template}'):
            shutil.copy(f'templates/{template}', f'public/{template}')
    
    print("Setup complete! To create a new post, run:")
    print("python3 scripts/prepare_post.py https://arxiv.org/html/paper-id")

if __name__ == "__main__":
    setup() 