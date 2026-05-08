"""
Game movement and floor progression event handlers
"""
import random
from flask import request
from flask_socketio import emit, join_room, leave_room
from game_state import players, game_rooms
from game.dungeon_generator import DungeonGenerator
from game.combat import Enemy
from game.lore_data import RARE_BOSSES
from cache_helpers import save_player_data, save_dungeon, load_dungeon, save_enemies, load_enemies
from config import Config

def register_game_handlers(socketio):
    """Register game-related socket handlers"""
    
    @socketio.on('move')
    def handle_move(data):
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        direction = data.get('direction')
        
        new_x, new_y = player.x, player.y
        if direction == 'up':
            new_y -= 1
        elif direction == 'down':
            new_y += 1
        elif direction == 'left':
            new_x -= 1
        elif direction == 'right':
            new_x += 1
        
        floor_key = f"floor_{player.floor}"
        dungeon = game_rooms[floor_key]['dungeon']
        
        # Check if move is valid
        if (0 <= new_x < dungeon.width and 
            0 <= new_y < dungeon.height and 
            dungeon.grid[new_y][new_x] == 0):
            
            player.x = new_x
            player.y = new_y
            
            emit('player_moved', {
                'player_id': player_id,
                'x': new_x,
                'y': new_y,
                'name': player.name
            }, room=floor_key, include_self=True)
            
            # Check for stairs
            stairs = game_rooms[floor_key]['entities']['stairs']
            if (player.x, player.y) == stairs:
                emit('reached_stairs', {'floor': player.floor})

    @socketio.on('descend_stairs')
    def handle_descend():
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        old_floor = f"floor_{player.floor}"
        leave_room(old_floor)
        
        player.floor += 1
        new_floor = f"floor_{player.floor}"
        
        # Generate new floor if needed
        if new_floor not in game_rooms:
            # Try to load from cache first
            cached_dungeon = load_dungeon(player.floor)
            cached_enemies = load_enemies(player.floor)
            
            if cached_dungeon and cached_enemies:
                # Restore from cache
                dungeon = DungeonGenerator(seed=cached_dungeon['seed'])
                dungeon.grid = cached_dungeon['grid']
                dungeon.width = cached_dungeon['width']
                dungeon.height = cached_dungeon['height']
                
                entities = cached_dungeon['entities']
                entities['spawn'] = tuple(entities['spawn'])
                entities['stairs'] = tuple(entities['stairs'])
                
                game_rooms[new_floor] = {
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
                    game_rooms[new_floor]['enemies'][enemy_id] = enemy
                
                if Config.FLASK_ENV == 'development':
                    print(f"[DEV] Floor {player.floor} restored from cache")
            else:
                # Generate new floor
                dungeon = DungeonGenerator(seed=random.randint(0, 999999))
                entities = dungeon.generate()
                game_rooms[new_floor] = {
                    'dungeon': dungeon,
                    'entities': entities,
                    'enemies': {}
                }
                
                # Spawn enemies
                for enemy_data in entities['enemies']:
                    enemy_id = f"enemy_{random.randint(0, 999999)}"
                    
                    # Check for boss spawn (every 5 floors)
                    is_boss = player.floor % 5 == 0 and len(game_rooms[new_floor]['enemies']) == 0
                    boss_data = None
                    
                    if is_boss:
                        suitable_bosses = [b for b in RARE_BOSSES if abs(b['level'] - player.floor) <= 3]
                        if suitable_bosses:
                            boss_data = random.choice(suitable_bosses)
                    
                    enemy = Enemy(player.floor, enemy_data['x'], enemy_data['y'], is_boss, boss_data)
                    game_rooms[new_floor]['enemies'][enemy_id] = enemy
                
                # Cache the new floor
                save_dungeon(player.floor, {
                    'seed': dungeon.seed,
                    'grid': dungeon.grid,
                    'width': dungeon.width,
                    'height': dungeon.height,
                    'entities': entities
                })
                
                save_enemies(player.floor, {
                    eid: e.to_dict() for eid, e in game_rooms[new_floor]['enemies'].items()
                })
                
                if Config.FLASK_ENV == 'development':
                    print(f"[DEV] Floor {player.floor} generated and cached")
        
        # Set player spawn
        spawn = game_rooms[new_floor]['entities']['spawn']
        player.x, player.y = spawn
        player.hp = player.max_hp  # Heal on floor change
        
        # Save player progress after completing floor
        save_player_data(player)
        if Config.FLASK_ENV == 'development':
            print(f"[DEV] Player {player.name} progress saved after completing floor {player.floor - 1}")
        
        join_room(new_floor)
        
        emit('floor_changed', {
            'floor': player.floor,
            'player': player.to_dict(),
            'dungeon': game_rooms[new_floor]['dungeon'].grid,
            'entities': game_rooms[new_floor]['entities'],
            'enemies': {eid: e.to_dict() for eid, e in game_rooms[new_floor]['enemies'].items()}
        })

    @socketio.on('upgrade_skill')
    def handle_upgrade_skill(data):
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        skill_name = data.get('skill')
        
        if player.upgrade_skill(skill_name):
            emit('skill_upgraded', {'player': player.to_dict()})

    @socketio.on('equip_item')
    def handle_equip(data):
        player_id = request.sid
        if player_id not in players:
            return
        
        player = players[player_id]
        item = data.get('item')
        
        if not player.can_equip(item):
            emit('equip_failed', {'reason': 'Level requirement not met'})
            return
        
        if item['type'] == 'weapon':
            player.weapon = item
        elif item['type'] == 'armor':
            player.armor = item
        
        # Save player data after equipping
        save_player_data(player)
        
        emit('item_equipped', {'player': player.to_dict()})

    @socketio.on('get_rare_weapons')
    def handle_get_rare_weapons():
        from game.lore_data import RARE_WEAPONS
        emit('rare_weapons_list', {'weapons': RARE_WEAPONS})

    @socketio.on('get_rare_bosses')
    def handle_get_rare_bosses():
        emit('rare_bosses_list', {'bosses': RARE_BOSSES})
