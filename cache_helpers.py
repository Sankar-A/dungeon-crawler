"""
Cache helper functions
"""
from cache import cache, CacheKeys
from config import Config

def save_player_data(player):
    """Save player data to cache and database"""
    from database import db
    
    if cache.enabled:
        cache.set(CacheKeys.player(player.id), player.to_dict(), ttl=Config.CACHE_PLAYER_TTL)
    
    if db.enabled:
        db.save_player(player)

def load_player_data(player_id):
    """Load player data from cache or database"""
    from database import db
    
    # Try cache first
    if cache.enabled:
        cached_data = cache.get(CacheKeys.player(player_id))
        if cached_data:
            if Config.FLASK_ENV == 'development':
                print(f"[DEV] Player {player_id} loaded from cache")
            return cached_data
    
    # Try database
    if db.enabled:
        db_data = db.load_player(player_id)
        if db_data:
            if Config.FLASK_ENV != 'development':
                # Cache it for next time in production only
                if cache.enabled:
                    cache.set(CacheKeys.player(player_id), db_data, ttl=Config.CACHE_PLAYER_TTL)
            return db_data
    
    return None

def save_loot_drop(loot_id, loot_data):
    """Save loot drop to cache"""
    if cache.enabled:
        cache.set(CacheKeys.loot(loot_id), loot_data, ttl=Config.CACHE_LOOT_TTL)

def load_loot_drop(loot_id):
    """Load loot drop from cache"""
    if cache.enabled:
        return cache.get(CacheKeys.loot(loot_id))
    return None

def delete_loot_drop(loot_id):
    """Delete loot drop from cache"""
    if cache.enabled:
        cache.delete(CacheKeys.loot(loot_id))

def save_dungeon(floor, dungeon_data):
    """Save dungeon layout to cache"""
    if cache.enabled:
        cache.set(CacheKeys.dungeon(floor), dungeon_data, ttl=Config.CACHE_DUNGEON_TTL)

def load_dungeon(floor):
    """Load dungeon layout from cache"""
    if cache.enabled:
        return cache.get(CacheKeys.dungeon(floor))
    return None

def save_enemies(floor, enemies_data):
    """Save enemies state to cache"""
    if cache.enabled:
        cache.set(CacheKeys.enemies(floor), enemies_data, ttl=Config.CACHE_ENEMIES_TTL)

def load_enemies(floor):
    """Load enemies state from cache"""
    if cache.enabled:
        return cache.get(CacheKeys.enemies(floor))
    return None

def load_all_loot_drops():
    """Load all loot drops from cache on startup"""
    from config import Config
    
    if not cache.enabled:
        return {}
    
    try:
        # Get all loot keys
        loot_keys = cache.client.keys('loot:*')
        if not loot_keys:
            return {}
        
        # Load all loot drops
        loot_data = {}
        for key in loot_keys:
            loot_id = key.split(':', 1)[1]  # Extract loot_id from "loot:{loot_id}"
            loot = cache.get(key)
            if loot:
                loot_data[loot_id] = loot
                if Config.FLASK_ENV == 'development':
                    print(f"[DEV] Restored loot {loot_id} from cache")
        
        return loot_data
    except Exception as e:
        if Config.FLASK_ENV != 'development':
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to load loot drops from cache: {e}")
        return {}
