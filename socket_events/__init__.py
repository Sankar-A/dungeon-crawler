"""
Socket event handlers package
"""
from .connection import register_connection_handlers
from .auth import register_auth_handlers
from .character import register_character_handlers
from .game import register_game_handlers
from .combat import register_combat_handlers
from .loot import register_loot_handlers

def register_all_handlers(socketio):
    """Register all socket event handlers"""
    register_connection_handlers(socketio)
    register_auth_handlers(socketio)
    register_character_handlers(socketio)
    register_game_handlers(socketio)
    register_combat_handlers(socketio)
    register_loot_handlers(socketio)

__all__ = ['register_all_handlers']
