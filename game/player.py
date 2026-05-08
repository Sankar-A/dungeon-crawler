import random
from typing import Dict, List

class Player:
    def __init__(self, player_id, name):
        self.id = player_id
        self.name = name
        self.level = 1
        self.xp = 0
        self.xp_to_next = 100
        
        # Stats
        self.max_hp = 100
        self.hp = 100
        self.strength = 10
        self.dexterity = 10
        self.intelligence = 10
        self.vitality = 10
        
        # Skills
        self.skill_points = 0
        self.skills = {
            'power_strike': 0,  # Increases damage
            'quick_reflexes': 0,  # Increases dodge
            'arcane_knowledge': 0,  # Increases magic damage
            'iron_skin': 0,  # Increases defense
            'critical_eye': 0,  # Increases crit chance
            'life_drain': 0  # Lifesteal
        }
        
        # Equipment
        self.weapon = None
        self.armor = None
        
        # Currency
        self.gold = 0
        
        # Position
        self.x = 0
        self.y = 0
        self.floor = 1
        
    def gain_xp(self, amount):
        """Gain XP and level up if threshold reached"""
        self.xp += amount
        leveled_up = False
        
        while self.xp >= self.xp_to_next:
            self.level_up()
            leveled_up = True
        
        return leveled_up
    
    def level_up(self):
        """Level up and increase stats"""
        self.xp -= self.xp_to_next
        self.level += 1
        self.xp_to_next = int(self.xp_to_next * 1.5)
        
        # Stat increases
        self.strength += 2
        self.dexterity += 2
        self.intelligence += 2
        self.vitality += 2
        self.max_hp += 20
        self.hp = self.max_hp
        
        # Skill points
        self.skill_points += 3
    
    def upgrade_skill(self, skill_name):
        """Upgrade a skill if player has points"""
        if skill_name in self.skills and self.skill_points > 0:
            self.skills[skill_name] += 1
            self.skill_points -= 1
            return True
        return False
    
    def calculate_damage(self):
        """Calculate total damage output"""
        base_damage = self.strength * 2
        weapon_damage = self.weapon['damage'] if self.weapon else 0
        skill_bonus = self.skills['power_strike'] * 5
        return base_damage + weapon_damage + skill_bonus
    
    def calculate_defense(self):
        """Calculate total defense"""
        base_defense = self.vitality
        armor_defense = self.armor['defense'] if self.armor else 0
        skill_bonus = self.skills['iron_skin'] * 3
        return base_defense + armor_defense + skill_bonus
    
    def take_damage(self, damage):
        """Take damage reduced by defense"""
        actual_damage = max(1, damage - self.calculate_defense())
        self.hp -= actual_damage
        return actual_damage
    
    def heal(self, amount):
        """Heal the player"""
        self.hp = min(self.max_hp, self.hp + amount)
    
    def can_equip(self, item):
        """Check if player meets level requirement"""
        return self.level >= item.get('min_level', 1)
    
    def get_weapon_range(self):
        """Get the attack range of current weapon"""
        if self.weapon:
            return self.weapon.get('range', 1)
        return 1  # Default melee range
    
    def is_ranged_weapon(self):
        """Check if current weapon is ranged"""
        if self.weapon:
            return self.weapon.get('ranged', False)
        return False
    
    def to_dict(self):
        """Convert player to dictionary for JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'level': self.level,
            'xp': self.xp,
            'xp_to_next': self.xp_to_next,
            'hp': self.hp,
            'max_hp': self.max_hp,
            'strength': self.strength,
            'dexterity': self.dexterity,
            'intelligence': self.intelligence,
            'vitality': self.vitality,
            'skill_points': self.skill_points,
            'skills': self.skills,
            'weapon': self.weapon,
            'armor': self.armor,
            'gold': self.gold,
            'x': self.x,
            'y': self.y,
            'floor': self.floor
        }
