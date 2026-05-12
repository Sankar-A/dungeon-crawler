"""
Loot management event handlers
"""
from flask import request
from flask_socketio import emit
from game_state import players, loot_drops
from cache_helpers import delete_loot_drop, save_player_data

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
        
        # Add items to player's inventory
        for item in loot['items']:
            player.inventory.append(item)
        
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

    @socketio.on('use_resistance_potion')
    def handle_use_resistance_potion(data):
        """Handle resistance potion usage from inventory"""
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        potion_index = data.get('potion_index')
        
        # Validate potion index
        if potion_index is None or potion_index < 0 or potion_index >= len(player.inventory):
            emit('resistance_potion_failed', {'reason': 'Invalid potion'})
            return
        
        potion = player.inventory[potion_index]
        
        # Validate it's a resistance potion
        if potion.get('type') != 'consumable' or potion.get('subtype') != 'resistance_potion':
            emit('resistance_potion_failed', {'reason': 'Not a resistance potion'})
            return
        
        # Apply resistance effect
        result = player.apply_resistance_potion(potion)
        
        if not result.get('success'):
            emit('resistance_potion_failed', {'reason': result.get('message', 'Failed to apply')})
            return
        
        # Remove potion from inventory
        player.inventory.pop(potion_index)
        
        # Save player data
        save_player_data(player)
        
        # Prepare event data
        floor_key = f"floor_{player.floor}"
        event_data = {
            'player_id': player_id,
            'player_name': player.name,
            'element': potion['element'],
            'reduction': potion['reduction'],
            'duration': potion['duration'],
            'player': player.to_dict()
        }
        
        # Include replaced element if applicable
        if result.get('replaced'):
            event_data['replaced_element'] = result.get('old_element')
        
        # Broadcast resistance activation to floor room
        emit('resistance_activated', event_data, room=floor_key)

    @socketio.on('discard_inventory_item')
    def handle_discard_inventory_item(data):
        """Handle discarding an item from player inventory"""
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        item_index = data.get('item_index')
        
        # Validate item index
        if item_index is None or item_index < 0 or item_index >= len(player.inventory):
            emit('discard_inventory_failed', {'reason': 'Invalid item index'})
            return
        
        # Get the item before removing it
        item = player.inventory[item_index]
        
        # Remove item from inventory
        player.inventory.pop(item_index)
        
        # Save player data
        save_player_data(player)
        
        # Send updated player state back
        emit('inventory_item_discarded', {
            'player': player.to_dict(),
            'item_name': item.get('name', 'Item')
        })
