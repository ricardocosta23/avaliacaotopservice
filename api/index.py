
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import the Flask app
from app import app

# For Vercel, the WSGI application must be directly available
# Vercel expects the app object to be directly accessible
if __name__ == "__main__":
    app.run()

