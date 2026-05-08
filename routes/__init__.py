"""
Routes package for HTTP endpoints
"""
from .main import main_bp
from .api import api_bp

__all__ = ['main_bp', 'api_bp']
