"""
Character management event handlers
"""
from flask import request
from flask_socketio import emit
from game_state import authenticated_users, players
from database import db
from game.player import Player
from .game_helpers import start_game

def register_character_handlers(socketio):
    """Register character-related socket handlers"""
    
    @socketio.on('create_character')
    def handle_create_character(data):
        """Create or load a character"""
        player_id = request.sid
        
        # Check authentication
        if player_id not in authenticated_users:
            emit('auth_required', {'reason': 'Not logged in'})
            return
        
        user = authenticated_users[player_id]
        name = data.get('name', '').strip()
        
        # Validate character name
        if not name or len(name) < 1 or len(name) > 10:
            emit('character_creation_failed', {'reason': 'Character name must be 1-10 characters'})
            return
        
        # Guest mode - skip database operations
        if user.get('is_guest'):
            # Create new player object directly
            player = Player(player_id, name, user['id'])
            players[player_id] = player
            start_game(player_id, player)
            return
        
        # Check if character already exists - if so, load it instead
        if db.enabled:
            existing_chars = db.get_user_characters(user['id'])
            existing_char = next((c for c in existing_chars if c['name'] == name), None)
            
            if existing_char:
                # Load existing character
                _load_existing_character(player_id, user, existing_char)
                return
        
        # Create new character in database
        if db.enabled:
            success = db.create_character(user['id'], name, player_id)
            if not success:
                emit('character_creation_failed', {'reason': 'Character limit reached (10 max) or name already used'})
                return
        
        # Create new player object
        player = Player(player_id, name, user['id'])
        players[player_id] = player
        
        # Start game with new character
        start_game(player_id, player)

    @socketio.on('delete_character')
    def handle_delete_character(data):
        """Delete a character"""
        session_id = request.sid
        
        if session_id not in authenticated_users:
            emit('auth_required', {'reason': 'Not logged in'})
            return
        
        user = authenticated_users[session_id]
        character_name = data.get('name', '').strip()
        
        if not character_name:
            emit('delete_failed', {'reason': 'Character name required'})
            return
        
        # Guest mode - cannot delete (no saved characters)
        if user.get('is_guest'):
            emit('delete_failed', {'reason': 'Guest mode - no saved characters'})
            return
        
        success = db.delete_character(user['id'], character_name)
        if success:
            emit('character_deleted', {'name': character_name})
        else:
            emit('delete_failed', {'reason': 'Character not found'})


def _load_existing_character(player_id, user, char_data):
    """Load an existing character from database"""
    # Create player object from saved data
    player = Player(player_id, char_data['name'], user['id'])
    player.level = char_data['level']
    player.xp = char_data['xp']
    player.gold = char_data['gold']
    player.floor = char_data['floor']
    player.x = char_data['x']
    player.y = char_data['y']
    player.hp = char_data['hp']
    player.max_hp = char_data['max_hp']
    player.weapon = char_data['weapon']
    player.armor = char_data['armor']
    player.skills = char_data['skills']
    player.skill_points = char_data['skill_points']
    
    players[player_id] = player
    
    # Start game with loaded character
    start_game(player_id, player)
