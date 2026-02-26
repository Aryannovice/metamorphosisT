"""
Vercel Serverless Function - Main API Entry Point
Routes all API requests to the FastAPI backend
"""
import sys
import os

# Add the workspace root to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root_dir)

# Load environment variables
from dotenv import load_dotenv
env_path = os.path.join(root_dir, 'backend', '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)

# Import the FastAPI app
from backend.main import app

# Vercel looks for 'app' variable
