"""
Global game state management
"""

# Game state (in-memory, with cache/db backing)
game_rooms = {}  # room_id -> game state
players = {}  # player_id -> Player object
loot_drops = {}  # loot_id -> { floor, x, y, items, gold }
combat_damage = {}  # enemy_id -> { player_id: damage_dealt }
authenticated_users = {}  # session_id -> user_data
