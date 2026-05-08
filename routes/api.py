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
