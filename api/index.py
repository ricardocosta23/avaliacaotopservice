import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app
from app import app

# Vercel expects the WSGI application to be named 'app'
# This is the entry point for Vercel
def handler(environ, start_response):
    return app(environ, start_response)

# For Vercel serverless functions, we need to export the app directly
# This ensures compatibility with Vercel's Python runtime
if __name__ == "__main__":
    app.run()
