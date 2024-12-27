#!/usr/bin/env python3
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

def find_free_port(start_port=8000, max_attempts=100):
    """Find a free port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socketserver.TCPServer(("", port), None) as s:
                return port
        except OSError:
            continue
    raise RuntimeError(f"Could not find a free port after {max_attempts} attempts")

def main():
    """Start a local server to preview the site"""
    # Get the absolute path to the public directory
    public_dir = Path(__file__).parent.parent / 'public'
    
    # Change to the public directory
    os.chdir(public_dir)
    
    # Find a free port
    try:
        PORT = find_free_port()
    except RuntimeError as e:
        print(f"Error: {e}")
        return
    
    # Set up the server
    Handler = http.server.SimpleHTTPRequestHandler
    
    print(f"\nStarting preview server at http://localhost:{PORT}")
    print("Press Ctrl+C to stop the server\n")
    
    # Open the browser
    webbrowser.open(f'http://localhost:{PORT}')
    
    # Start the server
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server...")
            httpd.shutdown()

if __name__ == '__main__':
    main() 