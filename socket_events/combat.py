"""
Combat event handlers
"""
import random
from flask import request
from flask_socketio import emit
from game_state import players, game_rooms, combat_damage, loot_drops
from game.combat import calculate_combat, generate_loot
from cache_helpers import save_loot_drop, save_enemies

def register_combat_handlers(socketio):
    """Register combat-related socket handlers"""
    
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
            
            # Generate loot
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
                'player': player.to_dict(),
                'enemy_id': enemy_id
            })
            
            # Broadcast enemy HP update to all players in the room
            emit('enemy_hp_updated', {
                'enemy_id': enemy_id,
                'hp': enemy.hp,
                'max_hp': enemy.max_hp
            }, room=floor_key)
