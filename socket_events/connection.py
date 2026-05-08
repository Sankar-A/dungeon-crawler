"""
Connection event handlers
"""
from flask import request
from flask_socketio import emit, leave_room
from game_state import players, authenticated_users
from database import db
from cache import cache, CacheKeys
from config import Config

def register_connection_handlers(socketio):
    """Register connection-related socket handlers"""
    
    @socketio.on('connect')
    def handle_connect():
        print(f'Client connected: {request.sid}')
        emit('connected', {'player_id': request.sid})

    @socketio.on('disconnect')
    def handle_disconnect():
        player_id = request.sid
        
        # Remove from authenticated users
        if player_id in authenticated_users:
            del authenticated_users[player_id]
        
        if player_id in players:
            player = players[player_id]
            room_id = f"floor_{player.floor}"
            
            # Save player data to database before disconnect
            if db.enabled:
                db.save_player(player)
            
            # Cache player data for quick reconnect
            if cache.enabled:
                cache.set(CacheKeys.player(player_id), player.to_dict(), ttl=Config.CACHE_PLAYER_TTL)
            
            leave_room(room_id)
            del players[player_id]
            emit('player_left', {'player_id': player_id}, room=room_id)
        print(f'Client disconnected: {player_id}')
