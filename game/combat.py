import random
from .lore_data import RARE_BOSSES

class Enemy:
    def __init__(self, level, x, y, is_boss=False, boss_data=None):
        self.level = level
        self.x = x
        self.y = y
        self.is_boss = is_boss
        
        if is_boss and boss_data:
            self.name = boss_data['name']
            self.hp = boss_data['hp']
            self.max_hp = boss_data['hp']
            self.damage = boss_data['damage']
            self.lore = boss_data['lore']
            self.drops = boss_data.get('drops', [])
        else:
            self.name = f"Level {level} Monster"
            self.max_hp = 50 + (level * 20)
            self.hp = self.max_hp
            self.damage = 10 + (level * 3)
            self.lore = None
            self.drops = []
    
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
            'lore': self.lore
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
        'dodged': False
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
        dodge_chance = 0.05 + (player.skills['quick_reflexes'] * 0.03)
        
        if random.random() < dodge_chance:
            result['dodged'] = True
        else:
            enemy_damage = enemy.damage
            actual_damage = player.take_damage(enemy_damage)
            result['enemy_damage'] = actual_damage
            result['player_hp'] = player.hp
            result['player_defeated'] = player.hp <= 0
            
            # Lifesteal
            if player.skills['life_drain'] > 0:
                lifesteal = int(actual_damage * (player.skills['life_drain'] * 0.1))
                player.heal(lifesteal)
                result['lifesteal'] = lifesteal
    
    return result

def generate_loot(enemy, player_level):
    """Generate loot from defeated enemy (no XP - that's distributed separately)"""
    loot = {
        'gold': random.randint(10, 30) * enemy.level,
        'items': []
    }
    
    # Boss drops rare weapons
    if enemy.is_boss and enemy.drops:
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
    """Generate random equipment based on level"""
    item_type = random.choice(['weapon', 'armor'])
    rarity = random.choices(['common', 'uncommon', 'rare'], weights=[70, 25, 5])[0]
    
    rarity_multiplier = {'common': 1, 'uncommon': 1.5, 'rare': 2}[rarity]
    
    if item_type == 'weapon':
        weapon_types = ['sword', 'axe', 'bow', 'dagger', 'staff']
        weapon_type = random.choice(weapon_types)
        
        # Determine if weapon is ranged
        ranged_types = ['bow', 'staff']
        is_ranged = weapon_type in ranged_types
        
        return {
            'type': 'weapon',
            'name': f"{rarity.title()} {weapon_type.title()}",
            'weapon_type': weapon_type,
            'damage': int((10 + level * 3) * rarity_multiplier),
            'min_level': max(1, level - 2),
            'rarity': rarity,
            'ranged': is_ranged,
            'range': 5 if is_ranged else 1
        }
    else:
        return {
            'type': 'armor',
            'name': f"{rarity.title()} Armor",
            'defense': int((5 + level * 2) * rarity_multiplier),
            'min_level': max(1, level - 2),
            'rarity': rarity
        }
