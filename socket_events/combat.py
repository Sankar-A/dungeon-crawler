"""
Combat event handlers
"""
import random
from flask import request
from flask_socketio import emit
from game_state import players, game_rooms, combat_damage, loot_drops
from game.combat import calculate_combat, generate_loot
from game.telegraph import telegraph_manager
from game import attack_zones
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
        
        # Get dungeon grid for zone calculations
        dungeon_grid = game_rooms[floor_key].get('dungeon', [])
        
        # Update player resistance (each turn)
        expired, expired_element = player.update_resistance()
        if expired:
            # Emit resistance expired event
            emit('resistance_expired', {
                'player_id': player_id,
                'player_name': player.name,
                'element': expired_element
            }, room=floor_key)
        
        # Calculate combat with telegraph support
        result = calculate_combat(player, enemy, telegraph_manager, dungeon_grid)
        result['is_ranged'] = player.is_ranged_weapon()
        result['distance'] = distance
        
        # Add avoidance and resistance information to result
        special_attack = result.get('special_attack')
        if special_attack:
            result['avoided'] = special_attack.get('avoided', False)
            result['resisted'] = special_attack.get('resisted', False)
            result['resistance_reduction'] = special_attack.get('resistance_reduction', 0.0)
            
            # Get attack zone tiles for visualization
            ability = enemy.telegraph_ability if hasattr(enemy, 'telegraph_ability') and enemy.telegraph_ability else None
            if ability:
                attack_zone_tiles = attack_zones.get_zone_tiles(
                    ability.get('attack_zone', {'type': 'none'}),
                    enemy,
                    dungeon_grid
                )
                result['attack_zone_tiles'] = [{'x': x, 'y': y} for x, y in attack_zone_tiles]
            else:
                result['attack_zone_tiles'] = []
        else:
            result['avoided'] = False
            result['resisted'] = False
            result['resistance_reduction'] = 0.0
            result['attack_zone_tiles'] = []
        
        # Track damage dealt by this player
        if enemy_id not in combat_damage:
            combat_damage[enemy_id] = {}
        if player_id not in combat_damage[enemy_id]:
            combat_damage[enemy_id][player_id] = 0
        combat_damage[enemy_id][player_id] += result['player_damage']
        
        # Handle telegraph events
        if result.get('telegraph_started'):
            telegraph_state = result['telegraph_started']
            ability = telegraph_state['ability']
            
            # Get attack zone tiles for visualization
            attack_zone_tiles = attack_zones.get_zone_tiles(
                ability.get('attack_zone', {'type': 'none'}),
                enemy,
                dungeon_grid
            )
            
            # Emit telegraph started event to floor room
            emit('telegraph_started', {
                'enemy_id': enemy_id,
                'boss_name': telegraph_state['boss_name'],
                'ability': {
                    'name': ability.get('name'),
                    'telegraph_turns': ability.get('telegraph_turns')
                },
                'boss_position': telegraph_state['boss_position'],
                'boss_facing': telegraph_state['boss_facing'],
                'attack_zone_tiles': [{'x': x, 'y': y} for x, y in attack_zone_tiles]
            }, room=floor_key)
        
        if result.get('telegraph_continuing'):
            # Emit telegraph updated event
            emit('telegraph_updated', {
                'enemy_id': enemy_id,
                'turns_remaining': result['telegraph_continuing']['turns_remaining']
            }, room=floor_key)
        
        if result.get('telegraph_executed'):
            # Emit telegraph ended event
            special_attack = result.get('special_attack', {})
            emit('telegraph_ended', {
                'enemy_id': enemy_id,
                'ability_name': result['telegraph_executed'],
                'execution_result': {
                    'damage': special_attack.get('damage', 0),
                    'avoided': special_attack.get('avoided', False),
                    'resisted': special_attack.get('resisted', False)
                }
            }, room=floor_key)
            
            # Emit attack_avoided event if attack was avoided
            if special_attack.get('avoided'):
                emit('attack_avoided', {
                    'player_id': player_id,
                    'player_name': player.name,
                    'ability_name': result['telegraph_executed'],
                    'reason': 'out_of_zone'
                }, room=floor_key)
            
            # Emit damage_resisted event if damage was resisted
            if special_attack.get('resisted'):
                from game.lore_data import get_ability_element
                element = get_ability_element(result['telegraph_executed'])
                reduction_amount = int(special_attack.get('damage', 0) * special_attack.get('resistance_reduction', 0.0))
                reduction_percent = int(special_attack.get('resistance_reduction', 0.0) * 100)
                
                emit('damage_resisted', {
                    'player_id': player_id,
                    'player_name': player.name,
                    'element': element,
                    'reduction_amount': reduction_amount,
                    'reduction_percent': reduction_percent
                }, room=floor_key)
        
        # Handle non-telegraphed special attacks (immediate execution)
        if special_attack and not result.get('telegraph_executed') and not result.get('telegraph_started'):
            ability_name = special_attack.get('ability', 'unknown')
            
            # Emit attack_avoided event if attack was avoided
            if special_attack.get('avoided'):
                emit('attack_avoided', {
                    'player_id': player_id,
                    'player_name': player.name,
                    'ability_name': ability_name,
                    'reason': 'out_of_zone'
                }, room=floor_key)
            
            # Emit damage_resisted event if damage was resisted
            if special_attack.get('resisted'):
                from game.lore_data import get_ability_element
                element = get_ability_element(ability_name)
                reduction_amount = int(special_attack.get('damage', 0) * special_attack.get('resistance_reduction', 0.0))
                reduction_percent = int(special_attack.get('resistance_reduction', 0.0) * 100)
                
                emit('damage_resisted', {
                    'player_id': player_id,
                    'player_name': player.name,
                    'element': element,
                    'reduction_amount': reduction_amount,
                    'reduction_percent': reduction_percent
                }, room=floor_key)
        
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
            
            # Cancel any active telegraph for this boss
            telegraph_manager.cancel_telegraph(id(enemy))
            
            # Emit telegraph cancelled if boss was telegraphing
            if hasattr(enemy, 'telegraph_active') and enemy.telegraph_active:
                emit('telegraph_cancelled', {
                    'enemy_id': enemy_id
                }, room=floor_key)
            
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
