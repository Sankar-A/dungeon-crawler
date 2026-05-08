"""
Configuration module for Dungeon Crawler
Loads settings from environment variables for security
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev_secret_key_change_in_production')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')
    
    # Redis Configuration
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379')
    REDIS_ENABLED = os.getenv('REDIS_ENABLED', 'true').lower() == 'true'
    
    # PostgreSQL Configuration
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost/dungeon_crawler')
    DATABASE_ENABLED = os.getenv('DATABASE_ENABLED', 'true').lower() == 'true'
    
    # Server Configuration
    PORT = int(os.getenv('PORT', 5000))
    HOST = os.getenv('HOST', '0.0.0.0')
    
    # Cache Configuration
    CACHE_PLAYER_TTL = int(os.getenv('CACHE_PLAYER_TTL', 3600))  # 1 hour
    CACHE_DUNGEON_TTL = int(os.getenv('CACHE_DUNGEON_TTL', 7200))  # 2 hours
    CACHE_LOOT_TTL = int(os.getenv('CACHE_LOOT_TTL', 1800))  # 30 minutes
    CACHE_ENEMIES_TTL = int(os.getenv('CACHE_ENEMIES_TTL', 1800))  # 30 minutes
    CACHE_LEADERBOARD_TTL = int(os.getenv('CACHE_LEADERBOARD_TTL', 300))  # 5 minutes
    
    @staticmethod
    def validate():
        """Validate critical configuration"""
        if Config.FLASK_ENV == 'production' and Config.SECRET_KEY == 'dev_secret_key_change_in_production':
            raise ValueError("SECRET_KEY must be set in production!")
        return True
