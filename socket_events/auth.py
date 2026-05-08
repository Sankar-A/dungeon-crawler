"""
Authentication event handlers
"""
from flask import request
from flask_socketio import emit
from game_state import authenticated_users
from database import db
import logging

logger = logging.getLogger(__name__)

def register_auth_handlers(socketio):
    """Register authentication-related socket handlers"""
    
    @socketio.on('register')
    def handle_register(data):
        """Register a new user account"""
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Check if database is disabled - use guest mode
        if not db.enabled:
            logger.info(f"Database disabled - creating guest user: {username}")
            guest_user = {
                'id': f'guest_{request.sid}',
                'username': username,
                'created_at': None,
                'last_login': None,
                'character_count': 0,
                'is_guest': True
            }
            authenticated_users[request.sid] = guest_user
            emit('register_success', {'user': guest_user, 'guest_mode': True})
            return
        
        # Validation
        if not username or len(username) < 3 or len(username) > 50:
            emit('register_failed', {'reason': 'Username must be 3-50 characters'})
            return
        
        if not password or len(password) < 6:
            emit('register_failed', {'reason': 'Password must be at least 6 characters'})
            return
        
        # Create user
        user = db.create_user(username, password)
        if not user:
            emit('register_failed', {'reason': 'Username already taken'})
            return
        
        # Store authenticated user
        authenticated_users[request.sid] = user
        
        emit('register_success', {'user': user})

    @socketio.on('login')
    def handle_login(data):
        """Login with username and password"""
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        # Check if database is disabled - use guest mode
        if not db.enabled:
            logger.info(f"Database disabled - creating guest user: {username}")
            guest_user = {
                'id': f'guest_{request.sid}',
                'username': username,
                'created_at': None,
                'last_login': None,
                'character_count': 0,
                'is_guest': True
            }
            authenticated_users[request.sid] = guest_user
            emit('login_success', {
                'user': guest_user,
                'characters': [],
                'guest_mode': True
            })
            return
        
        if not username or not password:
            emit('login_failed', {'reason': 'Username and password required'})
            return
        
        # Authenticate
        user = db.authenticate_user(username, password)
        if not user:
            emit('login_failed', {'reason': 'Invalid username or password'})
            return
        
        # Store authenticated user
        authenticated_users[request.sid] = user
        
        # Get user's characters
        characters = db.get_user_characters(user['id'])
        
        emit('login_success', {
            'user': user,
            'characters': characters
        })

    @socketio.on('get_characters')
    def handle_get_characters():
        """Get list of characters for logged-in user"""
        session_id = request.sid
        
        if session_id not in authenticated_users:
            emit('auth_required', {'reason': 'Not logged in'})
            return
        
        user = authenticated_users[session_id]
        
        # Guest mode - return empty list
        if user.get('is_guest'):
            emit('characters_list', {'characters': [], 'guest_mode': True})
            return
        
        characters = db.get_user_characters(user['id'])
        
        emit('characters_list', {'characters': characters})
