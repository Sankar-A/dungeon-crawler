import random
from .lore_data import RARE_BOSSES

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

def calculate_combat(player, enemy):
    """Simulate one round of combat"""
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
        'status_effects': []  # Track status effects applied
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
        # Boss special attacks (30% chance if cooldown is ready)
        if enemy.is_boss and hasattr(enemy, 'abilities') and enemy.abilities:
            if enemy.special_attack_cooldown <= 0 and random.random() < 0.3:
                special_result = execute_special_attack(enemy, player)
                result['special_attack'] = special_result
                result['enemy_damage'] = special_result.get('damage', 0)
                result['status_effects'] = special_result.get('status_effects', [])
                enemy.special_attack_cooldown = 3  # 3 turn cooldown
            else:
                # Normal attack
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
