"""
Attack zone calculation algorithms for boss special attacks
"""
import math


def is_player_in_zone(attack_zone_config, boss, player, dungeon_grid):
    """
    Main entry point for zone calculation
    
    Args:
        attack_zone_config: Dict with type and parameters
        boss: Enemy object with position and facing
        player: Player object with position
        dungeon_grid: 2D array of dungeon tiles (0=floor, 1=wall)
    
    Returns:
        bool: True if player is in attack zone
    """
    zone_type = attack_zone_config.get("type", "none")
    params = attack_zone_config.copy()
    params.pop("type", None)
    
    boss_pos = (boss.x, boss.y)
    player_pos = (player.x, player.y)
    
    if zone_type == "none":
        return True
    elif zone_type == "circle":
        return _calculate_circle(boss_pos, player_pos, params)
    elif zone_type == "cone":
        return _calculate_cone(boss_pos, player_pos, boss.facing_direction, params)
    elif zone_type == "line":
        return _calculate_line(boss_pos, player_pos, boss.facing_direction, params)
    elif zone_type == "aoe":
        return _calculate_aoe(boss_pos, player_pos, dungeon_grid, params)
    else:
        # Unknown zone type - default to always hit
        return True


def get_zone_tiles(attack_zone_config, boss, dungeon_grid):
    """
    Get list of all tiles in attack zone for visualization
    
    Args:
        attack_zone_config: Dict with type and parameters
        boss: Enemy object with position and facing
        dungeon_grid: 2D array of dungeon tiles (0=floor, 1=wall)
    
    Returns:
        List of (x, y) tuples representing affected tiles
    """
    zone_type = attack_zone_config.get("type", "none")
    params = attack_zone_config.copy()
    params.pop("type", None)
    
    boss_pos = (boss.x, boss.y)
    
    if zone_type == "none":
        return []  # No visualization for always-hit attacks
    elif zone_type == "circle":
        return _get_circle_tiles(boss_pos, params, dungeon_grid)
    elif zone_type == "cone":
        return _get_cone_tiles(boss_pos, boss.facing_direction, params, dungeon_grid)
    elif zone_type == "line":
        return _get_line_tiles(boss_pos, boss.facing_direction, params, dungeon_grid)
    elif zone_type == "aoe":
        return _get_aoe_tiles(boss_pos, dungeon_grid, params)
    else:
        return []


# Private helper functions for zone calculations
def _calculate_circle(boss_pos, player_pos, params):
    """Calculate if player is in circular zone"""
    bx, by = boss_pos
    px, py = player_pos
    radius = params.get("radius", 2)
    distance = math.sqrt((px - bx)**2 + (py - by)**2)
    return distance <= radius


def _calculate_cone(boss_pos, player_pos, facing, params):
    """Calculate if player is in 90-degree cone zone"""
    bx, by = boss_pos
    px, py = player_pos
    max_range = params.get("range", 3)
    
    dx = px - bx
    dy = py - by
    distance = max(abs(dx), abs(dy))  # Chebyshev distance
    
    if distance > max_range or distance == 0:
        return False
    
    # Check if within 90-degree cone based on facing
    if facing == "down":
        return dy > 0 and abs(dx) <= dy
    elif facing == "up":
        return dy < 0 and abs(dx) <= abs(dy)
    elif facing == "right":
        return dx > 0 and abs(dy) <= dx
    elif facing == "left":
        return dx < 0 and abs(dy) <= abs(dx)
    
    return False


def _calculate_line(boss_pos, player_pos, facing, params):
    """Calculate if player is in straight line zone"""
    bx, by = boss_pos
    px, py = player_pos
    max_range = params.get("range", 5)
    width = params.get("width", 1)
    
    dx = px - bx
    dy = py - by
    
    if facing in ["up", "down"]:
        # Vertical line
        if abs(dx) > width // 2:
            return False
        if facing == "down":
            return 0 < dy <= max_range
        else:  # up
            return -max_range <= dy < 0
    else:
        # Horizontal line
        if abs(dy) > width // 2:
            return False
        if facing == "right":
            return 0 < dx <= max_range
        else:  # left
            return -max_range <= dx < 0
    
    return False


def _calculate_aoe(boss_pos, player_pos, dungeon_grid, params):
    """Calculate if player is in AOE zone (entire room)"""
    return True  # Simplified - entire floor


# Private helper functions for tile visualization
def _get_circle_tiles(boss_pos, params, dungeon_grid):
    """Get all tiles in circular zone"""
    bx, by = boss_pos
    radius = params.get("radius", 2)
    tiles = []
    
    for x in range(int(bx - radius - 1), int(bx + radius + 2)):
        for y in range(int(by - radius - 1), int(by + radius + 2)):
            if math.sqrt((x - bx)**2 + (y - by)**2) <= radius:
                if _is_valid_tile(x, y, dungeon_grid):
                    tiles.append((x, y))
    
    return tiles


def _get_cone_tiles(boss_pos, facing, params, dungeon_grid):
    """Get all tiles in cone zone"""
    bx, by = boss_pos
    max_range = params.get("range", 3)
    tiles = []
    
    for x in range(bx - max_range, bx + max_range + 1):
        for y in range(by - max_range, by + max_range + 1):
            if _calculate_cone(boss_pos, (x, y), facing, params):
                if _is_valid_tile(x, y, dungeon_grid):
                    tiles.append((x, y))
    
    return tiles


def _get_line_tiles(boss_pos, facing, params, dungeon_grid):
    """Get all tiles in line zone"""
    bx, by = boss_pos
    max_range = params.get("range", 5)
    width = params.get("width", 1)
    tiles = []
    
    if facing in ["up", "down"]:
        for y in range(by - max_range, by + max_range + 1):
            for x in range(bx - width // 2, bx + width // 2 + 1):
                if _calculate_line(boss_pos, (x, y), facing, params):
                    if _is_valid_tile(x, y, dungeon_grid):
                        tiles.append((x, y))
    else:
        for x in range(bx - max_range, bx + max_range + 1):
            for y in range(by - width // 2, by + width // 2 + 1):
                if _calculate_line(boss_pos, (x, y), facing, params):
                    if _is_valid_tile(x, y, dungeon_grid):
                        tiles.append((x, y))
    
    return tiles


def _get_aoe_tiles(boss_pos, dungeon_grid, params):
    """Get all tiles in AOE zone (entire room)"""
    tiles = []
    height = len(dungeon_grid)
    width = len(dungeon_grid[0]) if height > 0 else 0
    
    for y in range(height):
        for x in range(width):
            if _is_valid_tile(x, y, dungeon_grid):
                tiles.append((x, y))
    
    return tiles


def _is_valid_tile(x, y, dungeon_grid):
    """Check if tile is within bounds and walkable (not a wall)"""
    if not dungeon_grid:
        return True
    
    height = len(dungeon_grid)
    width = len(dungeon_grid[0]) if height > 0 else 0
    
    if x < 0 or x >= width or y < 0 or y >= height:
        return False
    
    # 0 = floor (walkable), 1 = wall
    return dungeon_grid[y][x] == 0
