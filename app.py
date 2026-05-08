"""
Dungeon Crawler - Main Application
Multiplayer Procedural Dungeon RPG
"""
from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import logging
import sys
import traceback

# Configuration and core modules
from config import Config
from cache import cache
from database import db
from cache_helpers import load_all_loot_drops
from game_state import loot_drops

# Routes
from routes import main_bp, api_bp

# Socket event handlers
from socket_events import register_all_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Log startup
logger.info("=" * 60)
logger.info("DUNGEON CRAWLER - STARTING UP")
logger.info("=" * 60)

try:
    # Validate configuration
    logger.info("Validating configuration...")
    Config.validate()
    logger.info("Configuration validated successfully")
except Exception as e:
    logger.error(f"Configuration validation failed: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

try:
    logger.info("Creating Flask application...")
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    logger.info("Flask app created")
    
    logger.info("Initializing CORS...")
    CORS(app)
    logger.info("CORS initialized")
    
    logger.info("Initializing SocketIO...")
    socketio = SocketIO(app, cors_allowed_origins="*")
    logger.info("SocketIO initialized")
except Exception as e:
    logger.error(f"Failed to initialize Flask/SocketIO: {e}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    sys.exit(1)

# Register blueprints
app.register_blueprint(main_bp)
app.register_blueprint(api_bp)

# Register socket event handlers
register_all_handlers(socketio)

logger.info("=" * 60)
logger.info(f"Application started successfully")
logger.info(f"Environment: {Config.FLASK_ENV}")
logger.info(f"Redis Cache: {'Enabled' if cache.enabled else 'Disabled'}")
logger.info(f"PostgreSQL DB: {'Enabled' if db.enabled else 'Disabled'}")
logger.info("=" * 60)

if __name__ == '__main__':
    try:
        logger.info("=" * 60)
        logger.info("STARTING SERVER")
        logger.info("=" * 60)
        
        # Restore loot drops from cache on startup
        if cache.enabled:
            logger.info("Restoring loot drops from cache...")
            restored_loot = load_all_loot_drops()
            loot_drops.update(restored_loot)
            logger.info(f"Restored {len(restored_loot)} loot drops from cache")
            if Config.FLASK_ENV == 'development':
                print(f"[DEV] Restored {len(restored_loot)} loot drops from cache")
        
        logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
        logger.info(f"Redis Cache: {'Enabled' if cache.enabled else 'Disabled'}")
        logger.info(f"PostgreSQL DB: {'Enabled' if db.enabled else 'Disabled'}")
        logger.info("=" * 60)
        
        socketio.run(
            app, 
            host=Config.HOST, 
            port=Config.PORT, 
            debug=(Config.FLASK_ENV == 'development'),
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("=" * 60)
        logger.info("Shutting down gracefully...")
        logger.info("=" * 60)
    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"FATAL ERROR: {e}")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        logger.error("=" * 60)
        raise
    finally:
        # Cleanup
        logger.info("Cleaning up resources...")
        if cache.enabled:
            logger.info("Closing cache connection...")
            cache.close()
        if db.enabled:
            logger.info("Closing database connection...")
            db.close()
        logger.info("Server stopped")
        logger.info("=" * 60)
