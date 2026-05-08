"""
Cache module using Redis
Provides fast access to frequently used data
"""
import redis
import json
import logging
import traceback
from config import Config

logger = logging.getLogger(__name__)

class Cache:
    """Redis cache manager"""
    
    def __init__(self):
        self.client = None
        self.enabled = Config.REDIS_ENABLED
        self.is_dev = Config.FLASK_ENV == 'development'
        
        if self.enabled:
            try:
                logger.info("Initializing Redis cache...")
                redis_url = Config.REDIS_URL
                
                # Log connection attempt (without exposing password)
                safe_url = redis_url.split('@')[-1] if '@' in redis_url else 'local'
                logger.info(f"Connecting to Redis: {safe_url}")
                
                # Simple connection - Render handles TLS automatically
                self.client = redis.from_url(
                    redis_url,
                    decode_responses=True,
                    socket_connect_timeout=10,
                    socket_timeout=10
                )
                
                logger.info("Testing Redis connection...")
                # Test connection
                self.client.ping()
                logger.info("Redis connection successful")
                
                if self.is_dev:
                    print(f"[DEV] Redis cache initialized (operations will be simulated)")
                else:
                    logger.info("Redis cache initialized successfully")
            except Exception as e:
                logger.error(f"Redis initialization failed: {e}")
                logger.error(f"Error type: {type(e).__name__}")
                logger.error(f"Traceback: {traceback.format_exc()}")
                
                if self.is_dev:
                    print(f"[DEV] Redis initialization failed: {e} (will simulate operations)")
                else:
                    logger.info("Application will continue without cache")
                
                self.enabled = False
                self.client = None
    
    def get(self, key):
        """Get value from cache"""
        if not self.enabled or not self.client:
            return None
        
        try:
            if self.is_dev:
                print(f"[DEV] Cache GET: {key}")
                return None  # Simulate cache miss in dev
            
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            if not self.is_dev:
                logger.error(f"Cache get error: {e}")
            return None
    
    def set(self, key, value, ttl=None):
        """Set value in cache with optional TTL (seconds)"""
        if not self.enabled or not self.client:
            return False
        
        try:
            if self.is_dev:
                print(f"[DEV] Cache SET: {key} (TTL: {ttl}s)")
                return True  # Simulate success in dev
            
            serialized = json.dumps(value)
            if ttl:
                self.client.setex(key, ttl, serialized)
            else:
                self.client.set(key, serialized)
            return True
        except Exception as e:
            if not self.is_dev:
                logger.error(f"Cache set error: {e}")
            return False
    
    def delete(self, key):
        """Delete key from cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            if self.is_dev:
                print(f"[DEV] Cache DELETE: {key}")
                return True  # Simulate success in dev
            
            self.client.delete(key)
            return True
        except Exception as e:
            if not self.is_dev:
                logger.error(f"Cache delete error: {e}")
            return False
    
    def exists(self, key):
        """Check if key exists in cache"""
        if not self.enabled or not self.client:
            return False
        
        try:
            return self.client.exists(key) > 0
        except Exception as e:
            logger.error(f"Cache exists error: {e}")
            return False
    
    def increment(self, key, amount=1):
        """Increment a counter"""
        if not self.enabled or not self.client:
            return None
        
        try:
            return self.client.incrby(key, amount)
        except Exception as e:
            logger.error(f"Cache increment error: {e}")
            return None
    
    def get_many(self, keys):
        """Get multiple values at once"""
        if not self.enabled or not self.client:
            return {}
        
        try:
            values = self.client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = json.loads(value)
            return result
        except Exception as e:
            logger.error(f"Cache get_many error: {e}")
            return {}
    
    def set_many(self, mapping, ttl=None):
        """Set multiple key-value pairs"""
        if not self.enabled or not self.client:
            return False
        
        try:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                serialized = json.dumps(value)
                if ttl:
                    pipe.setex(key, ttl, serialized)
                else:
                    pipe.set(key, serialized)
            pipe.execute()
            return True
        except Exception as e:
            logger.error(f"Cache set_many error: {e}")
            return False
    
    def clear_pattern(self, pattern):
        """Delete all keys matching pattern (e.g., 'player:*')"""
        if not self.enabled or not self.client:
            return False
        
        try:
            keys = self.client.keys(pattern)
            if keys:
                self.client.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Cache clear_pattern error: {e}")
            return False
    
    def get_stats(self):
        """Get cache statistics"""
        if not self.enabled or not self.client:
            return {'enabled': False}
        
        try:
            info = self.client.info('stats')
            return {
                'enabled': True,
                'total_connections': info.get('total_connections_received', 0),
                'total_commands': info.get('total_commands_processed', 0),
                'keyspace_hits': info.get('keyspace_hits', 0),
                'keyspace_misses': info.get('keyspace_misses', 0),
                'used_memory': info.get('used_memory_human', 'N/A')
            }
        except Exception as e:
            logger.error(f"Cache stats error: {e}")
            return {'enabled': True, 'error': str(e)}
    
    def close(self):
        """Close Redis connection"""
        if self.client:
            self.client.close()


# Cache key helpers
class CacheKeys:
    """Cache key naming conventions"""
    
    @staticmethod
    def player(player_id):
        return f"player:{player_id}"
    
    @staticmethod
    def dungeon(floor):
        return f"dungeon:floor:{floor}"
    
    @staticmethod
    def enemies(floor):
        return f"enemies:floor:{floor}"
    
    @staticmethod
    def loot(loot_id):
        return f"loot:{loot_id}"
    
    @staticmethod
    def session(session_id):
        return f"session:{session_id}"
    
    @staticmethod
    def leaderboard():
        return "leaderboard:top"


# Global cache instance
cache = Cache()
