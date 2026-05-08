from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
import random
import json
import logging
from game.dungeon_generator import DungeonGenerator
from game.player import Player
from game.combat import Enemy, calculate_combat, generate_loot
from game.lore_data import RARE_BOSSES, RARE_WEAPONS
from config import Config
from cache import cache, CacheKeys
from database import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Validate configuration
Config.validate()

app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Game state (in-memory, with cache/db backing)
game_rooms = {}  # room_id -> game state
players = {}  # player_id -> Player object
loot_drops = {}  # loot_id -> { floor, x, y, items, gold }
combat_damage = {}  # enemy_id -> { player_id: damage_dealt }

logger.info(f"Application started - Redis: {cache.enabled}, Database: {db.enabled}")

# Restore loot drops from cache on startup
if cache.enabled:
    loot_drops = load_all_loot_drops()
    if Config.FLASK_ENV == 'development':
        print(f"[DEV] Restored {len(loot_drops)} loot drops from cache")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return {
        'status': 'healthy',
        'redis': cache.enabled,
        'database': db.enabled,
        'active_players': len(players),
        'active_rooms': len(game_rooms)
    }

@app.route('/stats')
def stats():
    """Statistics endpoint"""
    cache_stats = cache.get_stats() if cache.enabled else {'enabled': False}
    
    return {
        'cache': cache_stats,
        'game': {
            'active_players': len(players),
            'active_rooms': len(game_rooms),
            'loot_drops': len(loot_drops)
        }
    }

@app.route('/leaderboard')
def leaderboard():
    """Get top players leaderboard"""
    if db.enabled:
        # Try cache first
        cached = cache.get(CacheKeys.leaderboard()) if cache.enabled else None
        if cached:
            return {'leaderboard': cached, 'source': 'cache'}
        
        # Get from database
        leaders = db.get_leaderboard(limit=10)
        
        # Cache for 5 minutes
        if cache.enabled and leaders:
            cache.set(CacheKeys.leaderboard(), leaders, ttl=Config.CACHE_LEADERBOARD_TTL)
        
        return {'leaderboard': leaders, 'source': 'database'}
    else:
        # Fallback to in-memory players
        sorted_players = sorted(
            [p.to_dict() for p in players.values()],
            key=lambda x: (x['level'], x['xp']),
            reverse=True
        )[:10]
        return {'leaderboard': sorted_players, 'source': 'memory'}


# Helper functions
def save_player_data(player):
    """Save player data to cache and database"""
    if cache.enabled:
        cache.set(CacheKeys.player(player.id), player.to_dict(), ttl=Config.CACHE_PLAYER_TTL)
    
    if db.enabled:
        db.save_player(player)

def load_player_data(player_id):
    """Load player data from cache or database"""
    # Try cache first
    if cache.enabled:
        cached_data = cache.get(CacheKeys.player(player_id))
        if cached_data:
            if Config.FLASK_ENV == 'development':
                print(f"[DEV] Player {player_id} loaded from cache")
            return cached_data
    
    # Try database
    if db.enabled:
        db_data = db.load_player(player_id)
        if db_data:
            if Config.FLASK_ENV != 'development':
                # Cache it for next time in production only
                if cache.enabled:
                    cache.set(CacheKeys.player(player_id), db_data, ttl=Config.CACHE_PLAYER_TTL)
            return db_data
    
    return None

def save_loot_drop(loot_id, loot_data):
    """Save loot drop to cache"""
    if cache.enabled:
        cache.set(CacheKeys.loot(loot_id), loot_data, ttl=Config.CACHE_LOOT_TTL)

def load_loot_drop(loot_id):
    """Load loot drop from cache"""
    if cache.enabled:
        return cache.get(CacheKeys.loot(loot_id))
    return None

def delete_loot_drop(loot_id):
    """Delete loot drop from cache"""
    if cache.enabled:
        cache.delete(CacheKeys.loot(loot_id))

def save_dungeon(floor, dungeon_data):
    """Save dungeon layout to cache"""
    if cache.enabled:
        cache.set(CacheKeys.dungeon(floor), dungeon_data, ttl=Config.CACHE_DUNGEON_TTL)

def load_dungeon(floor):
    """Load dungeon layout from cache"""
    if cache.enabled:
        return cache.get(CacheKeys.dungeon(floor))
    return None

def save_enemies(floor, enemies_data):
    """Save enemies state to cache"""
    if cache.enabled:
        cache.set(CacheKeys.enemies(floor), enemies_data, ttl=Config.CACHE_ENEMIES_TTL)

def load_enemies(floor):
    """Load enemies state from cache"""
    if cache.enabled:
        return cache.get(CacheKeys.enemies(floor))
    return None

def load_all_loot_drops():
    """Load all loot drops from cache on startup"""
    if not cache.enabled:
        return {}
    
    try:
        # Get all loot keys
        loot_keys = cache.client.keys('loot:*')
        if not loot_keys:
            return {}
        
        # Load all loot drops
        loot_data = {}
        for key in loot_keys:
            loot_id = key.split(':', 1)[1]  # Extract loot_id from "loot:{loot_id}"
            loot = cache.get(key)
            if loot:
                loot_data[loot_id] = loot
                if Config.FLASK_ENV == 'development':
                    print(f"[DEV] Restored loot {loot_id} from cache")
        
        return loot_data
    except Exception as e:
        if Config.FLASK_ENV != 'development':
            logger.error(f"Failed to load loot drops from cache: {e}")
        return {}


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
        
        # Save player data to database before disconnect
        if db.enabled:
            db.save_player(player)
        
        # Cache player data for quick reconnect
        if cache.enabled:
            cache.set(CacheKeys.player(player_id), player.to_dict(), ttl=Config.CACHE_PLAYER_TTL)
        
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
        # Try to load from cache first
        cached_dungeon = load_dungeon(player.floor)
        cached_enemies = load_enemies(player.floor)
        
        if cached_dungeon and cached_enemies:
            # Restore from cache
            dungeon = DungeonGenerator(seed=cached_dungeon['seed'])
            dungeon.grid = cached_dungeon['grid']
            dungeon.width = cached_dungeon['width']
            dungeon.height = cached_dungeon['height']
            
            # Convert lists back to tuples for spawn/stairs (JSON serialization converts tuples to lists)
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
                enemy = Enemy(player.floor, enemy_data['x'], enemy_data['y'])
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
    
    # Check range
    distance = max(abs(player.x - enemy.x), abs(player.y - enemy.y))
    weapon_range = player.get_weapon_range()
    
    if distance > weapon_range:
        emit('attack_failed', {
            'reason': 'Out of range',
            'distance': distance,
            'range': weapon_range
        })
        return
    
    # Calculate combat
    result = calculate_combat(player, enemy)
    result['is_ranged'] = player.is_ranged_weapon()
    result['distance'] = distance
    
    # Track damage dealt by this player
    if enemy_id not in combat_damage:
        combat_damage[enemy_id] = {}
    if player_id not in combat_damage[enemy_id]:
        combat_damage[enemy_id][player_id] = 0
    combat_damage[enemy_id][player_id] += result['player_damage']
    
    if result['enemy_defeated']:
        # Calculate total XP from enemy
        total_xp = enemy.level * 25
        
        # Get all players who dealt damage
        damage_contributors = combat_damage.get(enemy_id, {})
        total_damage = sum(damage_contributors.values())
        
        # Distribute XP based on damage ratio
        xp_distribution = {}
        leveled_up_players = {}
        updated_players = {}
        
        for pid, damage_dealt in damage_contributors.items():
            if pid in players:
                xp_share = int(total_xp * (damage_dealt / total_damage))
                xp_distribution[pid] = xp_share
                leveled_up = players[pid].gain_xp(xp_share)
                leveled_up_players[pid] = leveled_up
                updated_players[pid] = players[pid].to_dict()
        
        # Generate loot (no XP in loot anymore)
        loot = generate_loot(enemy, player.level)
        
        # Create loot drop if there are items or gold
        loot_id = None
        if loot['items'] or loot['gold'] > 0:
            loot_id = f"loot_{player.floor}_{enemy.x}_{enemy.y}_{random.randint(0, 999999)}"
            loot_drops[loot_id] = {
                'id': loot_id,
                'floor': player.floor,
                'x': enemy.x,
                'y': enemy.y,
                'items': loot['items'],
                'gold': loot['gold']
            }
            # Cache the loot drop
            save_loot_drop(loot_id, loot_drops[loot_id])
        
        # Clean up damage tracking
        if enemy_id in combat_damage:
            del combat_damage[enemy_id]
        
        del game_rooms[floor_key]['enemies'][enemy_id]
        
        # Update enemies cache
        save_enemies(player.floor, {
            eid: e.to_dict() for eid, e in game_rooms[floor_key]['enemies'].items()
        })
        
        # Broadcast enemy defeat to all players in the room
        emit('enemy_defeated', {
            'enemy_id': enemy_id,
            'loot_drop': loot_drops.get(loot_id) if loot_id else None,
            'xp_distribution': xp_distribution,
            'leveled_up_players': leveled_up_players,
            'updated_players': updated_players,
            'is_ranged': result['is_ranged'],
            'attacker_id': player_id
        }, room=floor_key)
    else:
        # Send combat result to attacker
        emit('combat_result', {
            'result': result,
            'player': player.to_dict()
        })
        
        # Broadcast enemy HP update to all players in the room
        emit('enemy_hp_updated', {
            'enemy_id': enemy_id,
            'hp': enemy.hp,
            'max_hp': enemy.max_hp
        }, room=floor_key)

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
            
            # Convert lists back to tuples for spawn/stairs (JSON serialization converts tuples to lists)
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
                    # Find appropriate boss for this level
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
    emit('rare_weapons_list', {'weapons': RARE_WEAPONS})

@socketio.on('get_rare_bosses')
def handle_get_rare_bosses():
    emit('rare_bosses_list', {'bosses': RARE_BOSSES})

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
    
    # Give loot to player (no XP - that was already distributed)
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

if __name__ == '__main__':
    try:
        logger.info(f"Starting server on {Config.HOST}:{Config.PORT}")
        logger.info(f"Redis Cache: {'Enabled' if cache.enabled else 'Disabled'}")
        logger.info(f"PostgreSQL DB: {'Enabled' if db.enabled else 'Disabled'}")
        
        socketio.run(
            app, 
            host=Config.HOST, 
            port=Config.PORT, 
            debug=(Config.FLASK_ENV == 'development'),
            allow_unsafe_werkzeug=True
        )
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")
    finally:
        # Cleanup
        if cache.enabled:
            cache.close()
        if db.enabled:
            db.close()
        logger.info("Server stopped")

