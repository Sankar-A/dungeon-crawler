from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import random
import json
from game.dungeon_generator import DungeonGenerator
from game.player import Player
from game.combat import Enemy, calculate_combat, generate_loot
from game.lore_data import RARE_BOSSES, RARE_WEAPONS

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dungeon_crawler_secret_key_2026'
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Game state
game_rooms = {}  # room_id -> game state
players = {}  # player_id -> Player object

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print(f'Client connected: {request.sid}')
    emit('connected', {'player_id': request.sid})

@socketio.on('disconnect')
def handle_disconnect():
    player_id = request.sid
    if player_id in players:
        player = players[player_id]
        room_id = f"floor_{player.floor}"
        leave_room(room_id)
        del players[player_id]
        emit('player_left', {'player_id': player_id}, room=room_id)
    print(f'Client disconnected: {player_id}')

@socketio.on('create_character')
def handle_create_character(data):
    player_id = request.sid
    name = data.get('name', 'Adventurer')
    
    player = Player(player_id, name)
    players[player_id] = player
    
    # Generate first floor
    floor_key = f"floor_{player.floor}"
    if floor_key not in game_rooms:
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
            enemy = Enemy(player.floor, enemy_data['x'], enemy_data['y'])
            game_rooms[floor_key]['enemies'][enemy_id] = enemy
    
    # Set player spawn position
    spawn = game_rooms[floor_key]['entities']['spawn']
    player.x, player.y = spawn
    
    join_room(floor_key)
    
    emit('character_created', {
        'player': player.to_dict(),
        'dungeon': game_rooms[floor_key]['dungeon'].grid,
        'entities': game_rooms[floor_key]['entities'],
        'enemies': {eid: e.to_dict() for eid, e in game_rooms[floor_key]['enemies'].items()}
    })

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
            'y': new_y
        }, room=floor_key)
        
        # Check for stairs
        stairs = game_rooms[floor_key]['entities']['stairs']
        if (player.x, player.y) == stairs:
            emit('reached_stairs', {'floor': player.floor})

@socketio.on('attack_enemy')
def handle_attack(data):
    player_id = request.sid
    if player_id not in players:
        return
    
    player = players[player_id]
    enemy_id = data.get('enemy_id')
    floor_key = f"floor_{player.floor}"
    
    if enemy_id not in game_rooms[floor_key]['enemies']:
        return
    
    enemy = game_rooms[floor_key]['enemies'][enemy_id]
    
    # Calculate combat
    result = calculate_combat(player, enemy)
    
    if result['enemy_defeated']:
        loot = generate_loot(enemy, player.level)
        leveled_up = player.gain_xp(loot['xp'])
        
        del game_rooms[floor_key]['enemies'][enemy_id]
        
        emit('enemy_defeated', {
            'enemy_id': enemy_id,
            'loot': loot,
            'player': player.to_dict(),
            'leveled_up': leveled_up
        })
    else:
        emit('combat_result', {
            'result': result,
            'player': player.to_dict()
        })

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
                # Find appropriate boss for this level
                suitable_bosses = [b for b in RARE_BOSSES if abs(b['level'] - player.floor) <= 3]
                if suitable_bosses:
                    boss_data = random.choice(suitable_bosses)
            
            enemy = Enemy(player.floor, enemy_data['x'], enemy_data['y'], is_boss, boss_data)
            game_rooms[new_floor]['enemies'][enemy_id] = enemy
    
    # Set player spawn
    spawn = game_rooms[new_floor]['entities']['spawn']
    player.x, player.y = spawn
    player.hp = player.max_hp  # Heal on floor change
    
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
    
    emit('item_equipped', {'player': player.to_dict()})

@socketio.on('get_rare_weapons')
def handle_get_rare_weapons():
    emit('rare_weapons_list', {'weapons': RARE_WEAPONS})

@socketio.on('get_rare_bosses')
def handle_get_rare_bosses():
    emit('rare_bosses_list', {'bosses': RARE_BOSSES})

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
