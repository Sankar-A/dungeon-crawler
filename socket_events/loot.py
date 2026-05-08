"""
Loot management event handlers
"""
from flask import request
from flask_socketio import emit
from game_state import players, loot_drops
from cache_helpers import delete_loot_drop

def register_loot_handlers(socketio):
    """Register loot-related socket handlers"""
    
    @socketio.on('pickup_loot')
    def handle_pickup_loot(data):
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        loot_id = data.get('loot_id')
        
        if loot_id not in loot_drops:
            emit('pickup_failed', {'reason': 'Loot not found'})
            return
        
        loot = loot_drops[loot_id]
        
        # Check if loot is on the same floor
        if loot['floor'] != player.floor:
            emit('pickup_failed', {'reason': 'Loot on different floor'})
            return
        
        # Check range (5 tiles)
        distance = max(abs(player.x - loot['x']), abs(player.y - loot['y']))
        if distance > 5:
            emit('pickup_failed', {'reason': 'Too far away', 'distance': distance})
            return
        
        # Give loot to player
        player.gold += loot['gold']
        
        # Remove loot from global drops and cache
        del loot_drops[loot_id]
        delete_loot_drop(loot_id)
        
        # Broadcast loot pickup to all players in the room
        floor_key = f"floor_{player.floor}"
        emit('loot_picked_up', {
            'loot_id': loot_id,
            'player_id': player_id,
            'player': player.to_dict(),
            'items': loot['items'],
            'gold': loot['gold']
        }, room=floor_key)

    @socketio.on('discard_loot')
    def handle_discard_loot(data):
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        loot_id = data.get('loot_id')
        
        if loot_id not in loot_drops:
            emit('discard_failed', {'reason': 'Loot not found'})
            return
        
        loot = loot_drops[loot_id]
        
        # Check if loot is on the same floor
        if loot['floor'] != player.floor:
            emit('discard_failed', {'reason': 'Loot on different floor'})
            return
        
        # Check range (5 tiles)
        distance = max(abs(player.x - loot['x']), abs(player.y - loot['y']))
        if distance > 5:
            emit('discard_failed', {'reason': 'Too far away', 'distance': distance})
            return
        
        # Remove loot from global drops and cache
        del loot_drops[loot_id]
        delete_loot_drop(loot_id)
        
        # Broadcast loot discard to all players in the room
        floor_key = f"floor_{player.floor}"
        emit('loot_discarded', {
            'loot_id': loot_id,
            'player_id': player_id
        }, room=floor_key)
