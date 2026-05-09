"""
Configuration module for Dungeon Crawler
Loads settings from environment variables for security
"""
import os
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables from .env file
logger.info("Loading environment variables...")
load_dotenv()
logger.info("Environment variables loaded")

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
    
    # Testing/Debug Configuration
    FLOOR_1_BOSS = os.getenv('FLOOR_1_BOSS', None)  # Boss ID to spawn on floor 1 for testing
    
    @staticmethod
    def validate():
        """Validate critical configuration"""
        logger.info("Validating configuration...")
        logger.info(f"FLASK_ENV: {Config.FLASK_ENV}")
        logger.info(f"HOST: {Config.HOST}")
        logger.info(f"PORT: {Config.PORT}")
        logger.info(f"REDIS_ENABLED: {Config.REDIS_ENABLED}")
        logger.info(f"DATABASE_ENABLED: {Config.DATABASE_ENABLED}")
        
        if Config.FLASK_ENV == 'production':
            logger.info("Running in PRODUCTION mode")
            if Config.SECRET_KEY == 'dev_secret_key_change_in_production':
                logger.error("SECRET_KEY must be set in production!")
                raise ValueError("SECRET_KEY must be set in production!")
            logger.info("SECRET_KEY is properly configured")
        else:
            logger.info("Running in DEVELOPMENT mode")
        
        logger.info("Configuration validation complete")
        return True
