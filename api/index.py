"""
Vercel Serverless Function Entry Point for FastAPI Backend
"""
import sys
from pathlib import Path

# Add backend directory to path so we can import server
backend_path = str(Path(__file__).parent.parent / 'backend')
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

# Import the FastAPI app from server module
from server import app

# Export as 'app' for Vercel
__all__ = ['app']
