"""
Blink ability event handlers
"""
from flask import request
from flask_socketio import emit
from game_state import players, game_rooms


def register_blink_handlers(socketio):
    """Register blink-related socket handlers"""
    
    @socketio.on('activate_blink')
    def handle_activate_blink(data):
        """Handle blink ability activation"""
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        target_x = data.get('target_x')
        target_y = data.get('target_y')
        
        # Validate coordinates
        if target_x is None or target_y is None:
            emit('blink_failed', {'reason': 'Invalid target coordinates'})
            return
        
        # Get dungeon and enemies for current floor
        floor_key = f"floor_{player.floor}"
        if floor_key not in game_rooms:
            emit('blink_failed', {'reason': 'Floor not found'})
            return
        
        dungeon_grid = game_rooms[floor_key]['dungeon'].grid
        enemies = game_rooms[floor_key]['enemies']
        
        # Attempt blink
        result = player.activate_blink(target_x, target_y, dungeon_grid, enemies)
        
        if result['success']:
            # Broadcast blink activation to entire room
            emit('blink_activated', {
                'player_id': player_id,
                'player_name': player.name,
                'old_position': result['old_position'],
                'new_position': result['new_position'],
                'distance': result['distance']
            }, room=floor_key)
            
            # Send cooldown info to player
            emit('blink_cooldown_started', {
                'cooldown': result['cooldown'],
                'cooldown_end': player.blink_cooldown_end
            })
        else:
            # Send failure reason to player
            emit('blink_failed', {'reason': result['reason']})
    
    @socketio.on('get_blink_range')
    def handle_get_blink_range():
        """Get valid blink destination tiles"""
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        
        # Get blink config
        blink_config = player.get_blink_config()
        if not blink_config:
            emit('blink_range_response', {'valid_tiles': []})
            return
        
        # Get dungeon and enemies for current floor
        floor_key = f"floor_{player.floor}"
        if floor_key not in game_rooms:
            emit('blink_range_response', {'valid_tiles': []})
            return
        
        dungeon_grid = game_rooms[floor_key]['dungeon'].grid
        enemies = game_rooms[floor_key]['enemies']
        
        # Calculate valid tiles within range
        valid_tiles = _calculate_valid_blink_tiles(
            player, blink_config, dungeon_grid, enemies
        )
        
        emit('blink_range_response', {
            'valid_tiles': valid_tiles,
            'range': blink_config['range'],
            'through_enemies': blink_config['through_enemies']
        })


def _calculate_valid_blink_tiles(player, blink_config, dungeon_grid, enemies):
    """
    Calculate all valid blink destination tiles
    
    Args:
        player: Player object
        blink_config: Blink configuration dict
        dungeon_grid: 2D array of dungeon tiles
        enemies: Dict of enemy_id -> Enemy objects
    
    Returns:
        List of dicts with x, y coordinates
    """
    valid_tiles = []
    blink_range = blink_config['range']
    through_enemies = blink_config['through_enemies']
    
    # Get dungeon dimensions
    height = len(dungeon_grid)
    width = len(dungeon_grid[0]) if height > 0 else 0
    
    # Check all tiles within Chebyshev distance
    for y in range(max(0, player.y - blink_range), min(height, player.y + blink_range + 1)):
        for x in range(max(0, player.x - blink_range), min(width, player.x + blink_range + 1)):
            # Skip current position
            if x == player.x and y == player.y:
                continue
            
            # Check Chebyshev distance (max of dx, dy)
            distance = max(abs(x - player.x), abs(y - player.y))
            if distance > blink_range:
                continue
            
            # Check if tile is walkable
            if not _is_walkable_tile(x, y, dungeon_grid):
                continue
            
            # Check enemy occupation (unless Blink Master)
            if not through_enemies:
                enemy_present = False
                for enemy in enemies.values():
                    if enemy.x == x and enemy.y == y:
                        enemy_present = True
                        break
                
                if enemy_present:
                    continue
            
            # Valid tile
            valid_tiles.append({'x': x, 'y': y})
    
    return valid_tiles


def _is_walkable_tile(x, y, dungeon_grid):
    """
    Check if tile is walkable
    
    Args:
        x, y: Tile coordinates
        dungeon_grid: 2D array of dungeon tiles
    
    Returns:
        bool: True if tile is walkable
    """
    if not dungeon_grid:
        return True
    
    height = len(dungeon_grid)
    width = len(dungeon_grid[0]) if height > 0 else 0
    
    if x < 0 or x >= width or y < 0 or y >= height:
        return False
    
    # 1 = floor (walkable), 0 = wall
    return dungeon_grid[y][x] == 1
