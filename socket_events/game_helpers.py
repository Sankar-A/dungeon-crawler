"""
Helper functions for game socket handlers
"""
import random
from flask import request
from flask_socketio import emit, join_room
from game_state import players, game_rooms
from game.dungeon_generator import DungeonGenerator
from game.combat import Enemy
from game.lore_data import RARE_BOSSES
from cache_helpers import save_dungeon, load_dungeon, save_enemies, load_enemies
from config import Config

def start_game(player_id, player):
    """Start the game for a player (new or loaded character)"""
    # Generate or load floor
    floor_key = f"floor_{player.floor}"
    if floor_key not in game_rooms:
        # Try to load from cache first
        cached_dungeon = load_dungeon(player.floor)
        cached_enemies = load_enemies(player.floor)
        
        if cached_dungeon and cached_enemies:
            # Restore from cache
            dungeon = DungeonGenerator(seed=cached_dungeon['seed'])
            dungeon.grid = cached_dungeon['grid']
            dungeon.width = cached_dungeon['width']
            dungeon.height = cached_dungeon['height']
            
            # Convert lists back to tuples for spawn/stairs
            entities = cached_dungeon['entities']
            entities['spawn'] = tuple(entities['spawn'])
            entities['stairs'] = tuple(entities['stairs'])
            
            game_rooms[floor_key] = {
                'dungeon': dungeon,
                'entities': entities,
                'enemies': {}
            }
            
            # Restore enemies
            for enemy_id, enemy_data in cached_enemies.items():
                enemy = Enemy(enemy_data['level'], enemy_data['x'], enemy_data['y'])
                enemy.hp = enemy_data['hp']
                enemy.max_hp = enemy_data['max_hp']
                enemy.attack = enemy_data['attack']
                enemy.defense = enemy_data['defense']
                enemy.is_boss = enemy_data.get('is_boss', False)
                enemy.boss_data = enemy_data.get('boss_data')
                game_rooms[floor_key]['enemies'][enemy_id] = enemy
            
            if Config.FLASK_ENV == 'development':
                print(f"[DEV] Floor {player.floor} restored from cache")
        else:
            # Generate new floor
            dungeon = DungeonGenerator(seed=random.randint(0, 999999))
            entities = dungeon.generate()
            game_rooms[floor_key] = {
                'dungeon': dungeon,
                'entities': entities,
                'enemies': {}
            }
            
            # Spawn enemies
            for enemy_data in entities['enemies']:
                enemy_id = f"enemy_{random.randint(0, 999999)}"
                
                # Check for floor 1 boss override (testing/debug)
                if player.floor == 1 and Config.FLOOR_1_BOSS and len(game_rooms[floor_key]['enemies']) == 0:
                    # Spawn specific boss on floor 1 for testing
                    boss_data = next((b for b in RARE_BOSSES if b['id'] == Config.FLOOR_1_BOSS), None)
                    if boss_data:
                        enemy = Enemy(player.floor, enemy_data['x'], enemy_data['y'], True, boss_data)
                        game_rooms[floor_key]['enemies'][enemy_id] = enemy
                        if Config.FLASK_ENV == 'development':
                            print(f"[DEV] Spawned test boss '{boss_data['name']}' on floor 1")
                        continue  # Skip normal enemy spawn for this slot
                
                # Check for boss spawn (every 5 floors)
                is_boss = player.floor % 5 == 0 and len(game_rooms[floor_key]['enemies']) == 0
                boss_data = None
                
                if is_boss:
                    # Find appropriate boss for this level
                    suitable_bosses = [b for b in RARE_BOSSES if abs(b['level'] - player.floor) <= 3]
                    if suitable_bosses:
                        boss_data = random.choice(suitable_bosses)
                
                enemy = Enemy(player.floor, enemy_data['x'], enemy_data['y'], is_boss, boss_data)
                game_rooms[floor_key]['enemies'][enemy_id] = enemy
            
            # Cache the new floor
            save_dungeon(player.floor, {
                'seed': dungeon.seed,
                'grid': dungeon.grid,
                'width': dungeon.width,
                'height': dungeon.height,
                'entities': entities
            })
            
            save_enemies(player.floor, {
                eid: e.to_dict() for eid, e in game_rooms[floor_key]['enemies'].items()
            })
            
            if Config.FLASK_ENV == 'development':
                print(f"[DEV] Floor {player.floor} generated and cached")
    
    # Set player spawn position
    spawn = game_rooms[floor_key]['entities']['spawn']
    player.x, player.y = spawn
    
    join_room(floor_key)
    
    # Get other players on this floor
    other_players_data = {}
    for pid, p in players.items():
        if pid != player_id and p.floor == player.floor:
            other_players_data[pid] = {
                'x': p.x,
                'y': p.y,
                'name': p.name
            }
    
    emit('character_created', {
        'player': player.to_dict(),
        'dungeon': game_rooms[floor_key]['dungeon'].grid,
        'entities': game_rooms[floor_key]['entities'],
        'enemies': {eid: e.to_dict() for eid, e in game_rooms[floor_key]['enemies'].items()},
        'other_players': other_players_data
    })
    
    # Notify other players on this floor about new player
    emit('player_joined', {
        'player_id': player_id,
        'x': player.x,
        'y': player.y,
        'name': player.name
    }, room=floor_key, include_self=False)
