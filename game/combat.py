import random
from .lore_data import RARE_BOSSES, get_ability_element
from .attack_zones import is_player_in_zone
from .telegraph import telegraph_manager
from .attack_patterns import pattern_manager

class Enemy:
    def __init__(self, level, x, y, is_boss=False, boss_data=None):
        self.level = level
        self.x = x
        self.y = y
        self.is_boss = is_boss
        self.special_attack_cooldown = 0  # Tracks cooldown for special attacks
        
        if is_boss and boss_data:
            self.name = boss_data['name']
            self.hp = boss_data['hp']
            self.max_hp = boss_data['hp']
            self.damage = boss_data['damage']
            self.lore = boss_data['lore']
            self.drops = boss_data.get('drops', [])
            self.abilities = boss_data.get('abilities', [])
            self.boss_id = boss_data.get('id', '')
            
            # Telegraph state
            self.telegraph_active = False
            self.telegraph_ability = None
            self.telegraph_turns_remaining = 0
            
            # Attack pattern state
            self.attack_pattern_index = 0
            attack_pattern = boss_data.get('attack_pattern', {})
            self.attack_pattern_type = attack_pattern.get('type', 'predictable')
            self.attack_pattern_sequence = attack_pattern.get('sequence', [])
            
            # Facing direction for directional attacks
            self.facing_direction = 'down'
        else:
            # Exponential scaling for regular enemies
            # Base stats with exponential growth
            self.name = f"Level {level} Monster"
            
            # HP: 50 * (1.15 ^ level) - grows ~15% per level
            # Floor 1: ~58 HP, Floor 5: ~101 HP, Floor 10: ~203 HP, Floor 20: ~818 HP
            self.max_hp = int(50 * (1.15 ** level))
            self.hp = self.max_hp
            
            # Damage: 10 * (1.12 ^ level) - grows ~12% per level  
            # Floor 1: ~11 dmg, Floor 5: ~18 dmg, Floor 10: ~31 dmg, Floor 20: ~96 dmg
            self.damage = int(10 * (1.12 ** level))
            
            self.lore = None
            self.drops = []
            self.abilities = []
            self.boss_id = ''
    
    def take_damage(self, damage):
        self.hp -= damage
        return self.hp <= 0
    
    def to_dict(self):
        return {
            'name': self.name,
            'level': self.level,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'damage': self.damage,
            'x': self.x,
            'y': self.y,
            'is_boss': self.is_boss,
            'lore': self.lore,
            'abilities': self.abilities if hasattr(self, 'abilities') else []
        }

def calculate_combat(player, enemy, telegraph_manager_instance=None, dungeon_grid=None):
    """Simulate one round of combat with telegraph support"""
    result = {
        'player_damage': 0,
        'enemy_damage': 0,
        'player_hp': player.hp,
        'enemy_hp': enemy.hp,
        'enemy_defeated': False,
        'player_defeated': False,
        'critical': False,
        'dodged': False,
        'special_attack': None,  # Track if boss used special attack
        'status_effects': [],  # Track status effects applied
        'telegraph_started': None,
        'telegraph_executed': None,
        'telegraph_continuing': None
    }
    
    # Player attacks
    base_damage = player.calculate_damage()
    crit_chance = 0.1 + (player.skills['critical_eye'] * 0.05)
    
    if random.random() < crit_chance:
        result['critical'] = True
        base_damage *= 2
    
    result['player_damage'] = base_damage
    enemy_defeated = enemy.take_damage(base_damage)
    result['enemy_hp'] = enemy.hp
    result['enemy_defeated'] = enemy_defeated
    
    # Enemy attacks back if alive
    if not enemy_defeated:
        # Check if telegraph is active for boss
        if enemy.is_boss and hasattr(enemy, 'telegraph_active') and enemy.telegraph_active:
            # Update telegraph countdown
            if telegraph_manager_instance:
                should_execute = telegraph_manager_instance.update_telegraph(id(enemy))
                
                if should_execute:
                    # Execute telegraphed attack
                    ability = telegraph_manager_instance.execute_telegraph(id(enemy))
                    enemy.telegraph_active = False
                    enemy.telegraph_ability = None
                    enemy.telegraph_turns_remaining = 0
                    
                    if ability:
                        special_result = execute_special_attack_with_zones(
                            enemy, player, ability, dungeon_grid
                        )
                        result['special_attack'] = special_result
                        result['telegraph_executed'] = ability['name']
                        result['enemy_damage'] = special_result.get('damage', 0)
                        result['status_effects'] = special_result.get('status_effects', [])
                        result['player_hp'] = player.hp
                        result['player_defeated'] = player.hp <= 0
                    
                    # Set cooldown after execution
                    enemy.special_attack_cooldown = 3
                else:
                    # Still telegraphing - no attack this turn
                    enemy.telegraph_turns_remaining -= 1
                    result['telegraph_continuing'] = {
                        'ability': enemy.telegraph_ability['name'] if enemy.telegraph_ability else 'unknown',
                        'turns_remaining': enemy.telegraph_turns_remaining
                    }
        
        # Boss special attacks (if not telegraphing)
        elif enemy.is_boss and hasattr(enemy, 'abilities') and enemy.abilities:
            if enemy.special_attack_cooldown <= 0 and random.random() < 0.3:
                # Get next ability from pattern manager
                boss_data = next((b for b in RARE_BOSSES if b.get('id') == enemy.boss_id), None)
                
                if boss_data:
                    ability = pattern_manager.get_next_ability(id(enemy), boss_data)
                else:
                    # Fallback to random selection
                    ability = random.choice(enemy.abilities)
                
                # Check if ability has telegraph
                if ability and ability.get('telegraph_turns', 0) > 0:
                    # Start telegraph phase
                    if telegraph_manager_instance:
                        telegraph_state = telegraph_manager_instance.start_telegraph(
                            id(enemy), ability, enemy
                        )
                        result['telegraph_started'] = telegraph_state
                    else:
                        # No telegraph manager, execute immediately
                        special_result = execute_special_attack_with_zones(
                            enemy, player, ability, dungeon_grid
                        )
                        result['special_attack'] = special_result
                        result['enemy_damage'] = special_result.get('damage', 0)
                        result['status_effects'] = special_result.get('status_effects', [])
                        result['player_hp'] = player.hp
                        result['player_defeated'] = player.hp <= 0
                        enemy.special_attack_cooldown = 3
                else:
                    # Execute immediately (no telegraph)
                    if ability:
                        special_result = execute_special_attack_with_zones(
                            enemy, player, ability, dungeon_grid
                        )
                        result['special_attack'] = special_result
                        result['enemy_damage'] = special_result.get('damage', 0)
                        result['status_effects'] = special_result.get('status_effects', [])
                        result['player_hp'] = player.hp
                        result['player_defeated'] = player.hp <= 0
                    enemy.special_attack_cooldown = 3
            else:
                # Normal attack or cooldown
                if not (hasattr(enemy, 'telegraph_active') and enemy.telegraph_active):
                    enemy.special_attack_cooldown = max(0, enemy.special_attack_cooldown - 1)
                result.update(_normal_enemy_attack(player, enemy))
        else:
            # Regular enemy normal attack
            result.update(_normal_enemy_attack(player, enemy))
    
    return result


def _normal_enemy_attack(player, enemy):
    """Execute a normal enemy attack"""
    attack_result = {}
    dodge_chance = 0.05 + (player.skills['quick_reflexes'] * 0.03)
    
    if random.random() < dodge_chance:
        attack_result['dodged'] = True
    else:
        enemy_damage = enemy.damage
        actual_damage = player.take_damage(enemy_damage)
        attack_result['enemy_damage'] = actual_damage
        attack_result['player_hp'] = player.hp
        attack_result['player_defeated'] = player.hp <= 0
        
        # Lifesteal
        if player.skills['life_drain'] > 0:
            lifesteal = int(actual_damage * (player.skills['life_drain'] * 0.1))
            player.heal(lifesteal)
            attack_result['lifesteal'] = lifesteal
    
    return attack_result


def execute_special_attack(enemy, player):
    """Execute a boss special attack based on their abilities"""
    if not enemy.abilities:
        return {'damage': 0, 'ability': 'none'}
    
    ability = random.choice(enemy.abilities)
    result = {
        'ability': ability,
        'damage': 0,
        'status_effects': []
    }
    
    # Define special attack behaviors
    if ability == 'shadow_strike':
        # Ignores 50% of armor
        damage = int(enemy.damage * 1.5)
        defense = player.calculate_defense() // 2
        actual_damage = max(1, damage - defense)
        player.hp -= actual_damage
        result['damage'] = actual_damage
        result['description'] = f"{enemy.name} strikes from the shadows!"
        
    elif ability == 'darkness_aura':
        # Reduces player accuracy (simulated as guaranteed hit)
        damage = enemy.damage
        player.hp -= damage
        result['damage'] = damage
        result['status_effects'].append('blinded')
        result['description'] = f"{enemy.name} shrouds you in darkness!"
        
    elif ability == 'lightning_bolt' or ability == 'chain_lightning':
        # High damage electric attack
        damage = int(enemy.damage * 2)
        player.hp -= damage
        result['damage'] = damage
        result['description'] = f"{enemy.name} strikes with lightning!"
        
    elif ability == 'thunder_clap':
        # AOE stun effect (simulated as extra damage)
        damage = int(enemy.damage * 1.3)
        player.hp -= damage
        result['damage'] = damage
        result['status_effects'].append('stunned')
        result['description'] = f"{enemy.name} unleashes a thunderous roar!"
        
    elif ability == 'frost_nova':
        # Freeze and damage
        damage = enemy.damage
        player.hp -= damage
        result['damage'] = damage
        result['status_effects'].append('frozen')
        result['description'] = f"{enemy.name} freezes you solid!"
        
    elif ability == 'death_coil':
        # Damage and heal enemy
        damage = int(enemy.damage * 1.2)
        player.hp -= damage
        heal_amount = damage // 2
        enemy.hp = min(enemy.max_hp, enemy.hp + heal_amount)
        result['damage'] = damage
        result['enemy_healed'] = heal_amount
        result['description'] = f"{enemy.name} drains your life force!"
        
    elif ability == 'flame_burst' or ability == 'inferno':
        # Fire damage over time
        damage = int(enemy.damage * 1.8)
        player.hp -= damage
        result['damage'] = damage
        result['status_effects'].append('burning')
        result['description'] = f"{enemy.name} engulfs you in flames!"
        
    elif ability == 'void_tentacles':
        # Multiple hits
        total_damage = 0
        for _ in range(3):
            hit_damage = enemy.damage // 2
            player.hp -= hit_damage
            total_damage += hit_damage
        result['damage'] = total_damage
        result['description'] = f"{enemy.name} lashes out with void tentacles!"
        
    elif ability == 'reality_tear':
        # Massive damage, ignores armor
        damage = int(enemy.damage * 2.5)
        player.hp -= damage
        result['damage'] = damage
        result['description'] = f"{enemy.name} tears through reality itself!"
        
    elif ability == 'poison_breath' or ability == 'venom_spit':
        # Poison damage
        damage = enemy.damage
        player.hp -= damage
        result['damage'] = damage
        result['status_effects'].append('poisoned')
        result['description'] = f"{enemy.name} spits deadly venom!"
        
    elif ability == 'dragon_breath':
        # Cone of fire
        damage = int(enemy.damage * 2.2)
        player.hp -= damage
        result['damage'] = damage
        result['description'] = f"{enemy.name} breathes scorching fire!"
        
    elif ability == 'tail_sweep' or ability == 'wing_buffet':
        # Knockback damage
        damage = int(enemy.damage * 1.4)
        player.hp -= damage
        result['damage'] = damage
        result['status_effects'].append('knocked_back')
        result['description'] = f"{enemy.name} sends you flying!"
        
    elif ability == 'soul_harvest' or ability == 'reap':
        # Execute-style attack (more damage if low HP)
        hp_percent = player.hp / player.max_hp
        damage_multiplier = 2.0 if hp_percent < 0.3 else 1.5
        damage = int(enemy.damage * damage_multiplier)
        player.hp -= damage
        result['damage'] = damage
        result['description'] = f"{enemy.name} reaps your soul!"
        
    elif ability == 'chaos_bolt':
        # Random damage
        damage = random.randint(enemy.damage // 2, enemy.damage * 3)
        player.hp -= damage
        result['damage'] = damage
        result['description'] = f"{enemy.name} hurls chaotic energy!"
        
    elif ability == 'blood_rage' or ability == 'berserker':
        # Increased damage, enemy takes damage too
        damage = int(enemy.damage * 2)
        player.hp -= damage
        enemy.hp -= enemy.damage // 4  # Boss hurts itself
        result['damage'] = damage
        result['description'] = f"{enemy.name} enters a blood frenzy!"
        
    else:
        # Default special attack
        damage = int(enemy.damage * 1.5)
        player.hp -= damage
        result['damage'] = damage
        result['description'] = f"{enemy.name} uses {ability}!"
    
    result['player_defeated'] = player.hp <= 0
    return result


def execute_special_attack_with_zones(enemy, player, ability, dungeon_grid=None):
    """
    Execute a boss special attack with zone checking and resistance application
    
    Args:
        enemy: Enemy object with position and facing
        player: Player object with position and resistance
        ability: Ability dict with attack_zone, element, damage_multiplier, special_effects
        dungeon_grid: 2D array of dungeon tiles (optional)
    
    Returns:
        dict: Result with damage, status_effects, avoided, resisted, resistance_reduction, description
    """
    result = {
        'ability': ability.get('name', 'unknown'),
        'damage': 0,
        'status_effects': [],
        'avoided': False,
        'resisted': False,
        'resistance_reduction': 0.0,
        'description': ''
    }
    
    # Check if player is in attack zone
    attack_zone = ability.get('attack_zone', {'type': 'none'})
    if attack_zone.get('type') != 'none':
        in_zone = is_player_in_zone(attack_zone, enemy, player, dungeon_grid)
        if not in_zone:
            result['avoided'] = True
            result['description'] = f"{enemy.name} uses {ability.get('name')} but you avoided it!"
            return result
    
    # Calculate base damage
    damage_multiplier = ability.get('damage_multiplier', 1.0)
    base_damage = int(enemy.damage * damage_multiplier)
    
    # Apply armor penetration if present
    special_effects = ability.get('special_effects', {})
    armor_penetration = special_effects.get('armor_penetration', 0.0)
    
    if armor_penetration > 0:
        defense = player.calculate_defense()
        reduced_defense = int(defense * (1.0 - armor_penetration))
        actual_damage = max(1, base_damage - reduced_defense)
    else:
        actual_damage = max(1, base_damage - player.calculate_defense())
    
    # Apply resistance reduction
    element = get_ability_element(ability.get('name', ''))
    resistance_reduction = player.calculate_resistance_reduction(element)
    
    if resistance_reduction > 0:
        result['resisted'] = True
        result['resistance_reduction'] = resistance_reduction
        actual_damage = int(actual_damage * (1.0 - resistance_reduction))
    
    # Apply damage to player
    player.hp -= actual_damage
    result['damage'] = actual_damage
    result['player_defeated'] = player.hp <= 0
    
    # Apply status effects
    if special_effects.get('blind'):
        result['status_effects'].append('blinded')
    if special_effects.get('freeze'):
        result['status_effects'].append('frozen')
    if special_effects.get('stun'):
        result['status_effects'].append('stunned')
    if special_effects.get('poison'):
        result['status_effects'].append('poisoned')
    if special_effects.get('burn'):
        result['status_effects'].append('burning')
    
    # Handle special behaviors
    if special_effects.get('heal_boss'):
        heal_multiplier = special_effects.get('heal_boss')
        if isinstance(heal_multiplier, bool):
            heal_multiplier = 0.5
        heal_amount = int(actual_damage * heal_multiplier)
        enemy.hp = min(enemy.max_hp, enemy.hp + heal_amount)
        result['enemy_healed'] = heal_amount
    
    # Build description
    ability_name = ability.get('name', 'special attack')
    result['description'] = f"{enemy.name} uses {ability_name}!"
    
    if result['resisted']:
        reduction_percent = int(resistance_reduction * 100)
        result['description'] += f" (Reduced by {reduction_percent}%)"
    
    return result


def generate_resistance_potion():
    """
    Generate a random resistance potion
    
    Returns:
        dict: Resistance potion item with element, reduction, duration
    """
    elements = ['fire', 'frost', 'lightning', 'poison', 'shadow', 'holy', 'void']
    element = random.choice(elements)
    
    # Random strength: 30-50%
    reduction = round(random.uniform(0.30, 0.50), 2)
    
    # Random duration: 3-5 turns
    duration = random.randint(3, 5)
    
    # Format element name for display
    element_name = element.title()
    reduction_percent = int(reduction * 100)
    
    return {
        'type': 'consumable',
        'subtype': 'resistance_potion',
        'name': f'{element_name} Resistance Potion',
        'element': element,
        'reduction': reduction,
        'duration': duration,
        'rarity': 'uncommon',
        'description': f'Reduces {element} damage by {reduction_percent}% for {duration} turns'
    }


def generate_loot(enemy, player_level):
    """Generate loot from defeated enemy (no XP - that's distributed separately)"""
    # Exponential gold scaling: 20 * (1.13 ^ level)
    # Slightly lower than enemy HP growth (1.15) to maintain challenge
    base_gold = int(20 * (1.13 ** enemy.level))
    loot = {
        'gold': random.randint(int(base_gold * 0.8), int(base_gold * 1.2)),
        'items': []
    }
    
    # Check for guaranteed legendary drop (special bonus room bosses)
    if hasattr(enemy, 'guaranteed_legendary') and enemy.guaranteed_legendary:
        from .lore_data import RARE_WEAPONS
        # Always drop a legendary weapon appropriate for the level
        suitable_weapons = [w for w in RARE_WEAPONS if abs(w['level'] - player_level) <= 5]
        if suitable_weapons:
            legendary_weapon = random.choice(suitable_weapons)
            loot['items'].append(legendary_weapon)
        # Extra gold for legendary boss
        loot['gold'] *= 3
    
    # Boss drops rare weapons
    elif enemy.is_boss and enemy.drops:
        from .lore_data import RARE_WEAPONS
        for weapon_id in enemy.drops:
            weapon = next((w for w in RARE_WEAPONS if w['id'] == weapon_id), None)
            if weapon:
                loot['items'].append(weapon)
    
    # Regular drops
    elif random.random() < 0.3:
        loot['items'].append(generate_random_item(player_level))
    
    # Resistance potion drops
    if enemy.is_boss:
        # Boss: 50% chance per potion, 2-3 potions
        num_potions = random.randint(2, 3)
        for _ in range(num_potions):
            if random.random() < 0.5:
                loot['items'].append(generate_resistance_potion())
    elif hasattr(enemy, 'is_elite') and enemy.is_elite:
        # Elite: 15% chance for 1 potion
        if random.random() < 0.15:
            loot['items'].append(generate_resistance_potion())
    else:
        # Common: 5% chance for 1 potion
        if random.random() < 0.05:
            loot['items'].append(generate_resistance_potion())
    
    return loot


def generate_random_item(level):
    """Generate random equipment based on level with exponential scaling"""
    item_type = random.choice(['weapon', 'armor'])
    rarity = random.choices(['common', 'uncommon', 'rare'], weights=[70, 25, 5])[0]
    
    rarity_multiplier = {'common': 1, 'uncommon': 1.5, 'rare': 2}[rarity]
    
    if item_type == 'weapon':
        weapon_types = ['sword', 'axe', 'bow', 'dagger', 'staff']
        weapon_type = random.choice(weapon_types)
        
        # Determine if weapon is ranged
        ranged_types = ['bow', 'staff']
        is_ranged = weapon_type in ranged_types
        
        # Exponential weapon damage: 10 * (1.10 ^ level) * rarity
        # Growth rate 1.10 vs enemy damage 1.12 - weapons slightly weaker
        base_damage = int(10 * (1.10 ** level) * rarity_multiplier)
        
        return {
            'type': 'weapon',
            'name': f"{rarity.title()} {weapon_type.title()}",
            'weapon_type': weapon_type,
            'damage': base_damage,
            'min_level': max(1, level - 2),
            'rarity': rarity,
            'ranged': is_ranged,
            'range': 5 if is_ranged else 1
        }
    else:
        # Exponential armor defense: 5 * (1.10 ^ level) * rarity
        # Same growth rate as weapons for consistency
        base_defense = int(5 * (1.10 ** level) * rarity_multiplier)
        
        return {
            'type': 'armor',
            'name': f"{rarity.title()} Armor",
            'defense': base_defense,
            'min_level': max(1, level - 2),
            'rarity': rarity
        }
