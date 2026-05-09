"""
API routes for health checks and statistics
"""
from flask import Blueprint
from game_state import players, game_rooms
from cache import cache
from database import db

api_bp = Blueprint('api', __name__)

@api_bp.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'redis': cache.enabled,
        'database': db.enabled,
        'active_players': len(players),
        'active_rooms': len(game_rooms)
    }

@api_bp.route('/stats')
def stats():
    """Statistics endpoint"""
    cache_stats = cache.get_stats() if cache.enabled else {'enabled': False}
    
    return {
        'cache': cache_stats,
        'game': {
            'active_players': len(players),
            'active_rooms': len(game_rooms),
            'loot_drops': 0  # Will be updated when we refactor loot
        }
    }

@api_bp.route('/leaderboard')
def leaderboard():
    """Get top players leaderboard"""
    from config import Config
    
    if db.enabled:
        # Try cache first
        from cache import CacheKeys
        cached = cache.get(CacheKeys.leaderboard()) if cache.enabled else None
        if cached:
            return {'leaderboard': cached, 'source': 'cache'}
        
        # Get from database
        leaders = db.get_leaderboard(limit=10)
        
        # Cache for 5 minutes
        if cache.enabled and leaders:
            cache.set(CacheKeys.leaderboard(), leaders, ttl=Config.CACHE_LEADERBOARD_TTL)
        
        return {'leaderboard': leaders, 'source': 'database'}
    else:
        # Fallback to in-memory players
        sorted_players = sorted(
            [p.to_dict() for p in players.values()],
            key=lambda x: (x['level'], x['xp']),
            reverse=True
        )[:10]
        return {'leaderboard': sorted_players, 'source': 'memory'}

@api_bp.route('/cache/<key>')
def get_cache_key(key):
    """Get a specific cache key value"""
    if not cache.enabled:
        return {'error': 'Cache is not enabled'}, 503
    
    value = cache.get(key)
    if value is None:
        return {'error': 'Key not found', 'key': key}, 404
    
    return {
        'key': key,
        'value': value,
        'exists': True
    }

@api_bp.route('/cache')
def list_cache_keys():
    """List all cache keys (pattern-based)"""
    if not cache.enabled:
        return {'error': 'Cache is not enabled'}, 503
    
    if not cache.client:
        return {'error': 'Cache client not available'}, 503
    
    try:
        # Get all keys (use with caution in production with many keys)
        all_keys = cache.client.keys('*')
        
        # Group keys by prefix
        grouped = {}
        for key in all_keys:
            prefix = key.split(':')[0] if ':' in key else 'other'
            if prefix not in grouped:
                grouped[prefix] = []
            grouped[prefix].append(key)
        
        return {
            'total_keys': len(all_keys),
            'keys_by_prefix': grouped,
            'all_keys': all_keys
        }
    except Exception as e:
        return {'error': str(e)}, 500

@api_bp.route('/db/<table>')
def get_db_table(table):
    """Get all records from a database table"""
    if not db.enabled:
        return {'error': 'Database is not enabled'}, 503
    
    # Map table names to models
    from database import User, PlayerData, GameStats
    
    table_map = {
        'users': User,
        'players': PlayerData,
        'game_stats': GameStats
    }
    
    if table not in table_map:
        return {
            'error': 'Invalid table name',
            'valid_tables': list(table_map.keys())
        }, 400
    
    try:
        session = db.get_session()
        model = table_map[table]
        records = session.query(model).all()
        
        # Convert to dict, handling password fields
        result = []
        for record in records:
            record_dict = record.to_dict()
            # Remove sensitive data
            if table == 'users' and 'password_hash' in record_dict:
                record_dict.pop('password_hash', None)
            result.append(record_dict)
        
        session.close()
        
        return {
            'table': table,
            'count': len(result),
            'records': result
        }
    except Exception as e:
        if session:
            session.close()
        return {'error': str(e)}, 500

@api_bp.route('/db')
def list_db_tables():
    """List all available database tables"""
    if not db.enabled:
        return {'error': 'Database is not enabled'}, 503
    
    from database import User, PlayerData, GameStats
    
    try:
        session = db.get_session()
        
        tables_info = {
            'users': session.query(User).count(),
            'players': session.query(PlayerData).count(),
            'game_stats': session.query(GameStats).count()
        }
        
        session.close()
        
        return {
            'tables': list(tables_info.keys()),
            'record_counts': tables_info
        }
    except Exception as e:
        if session:
            session.close()
        return {'error': str(e)}, 500
