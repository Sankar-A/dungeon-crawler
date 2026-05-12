import random
import time
from typing import Dict, List, Tuple, Optional

class Player:
    def __init__(self, player_id, name, user_id=None):
        self.id = player_id
        self.name = name
        self.user_id = user_id
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
            'life_drain': 0,  # Lifesteal
            'blink': 0  # 0-4 for blink levels (0=locked, 1-4=Blink I-Master)
        }
        
        # Blink ability
        self.blink_level = 0  # 0 = locked, 1-4 = Blink I-Master
        self.blink_cooldown_end = 0  # Unix timestamp in seconds
        
        # Equipment
        self.weapon = None
        self.armor = None
        
        # Inventory
        self.inventory = []
        
        # Currency
        self.gold = 0
        
        # Position
        self.x = 0
        self.y = 0
        self.floor = 1
        
        # Active resistance effect
        self.active_resistance = None  # None or resistance dict
        
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
        if self.skill_points <= 0:
            return False
        
        # Handle blink skill upgrades (sequential unlock)
        if skill_name == 'blink':
            current_level = self.skills.get('blink', 0)
            if current_level >= 4:
                return False  # Max level reached
            
            self.skills['blink'] = current_level + 1
            self.skill_points -= 1
            return True
        
        # Check if it's a skill
        if skill_name in self.skills:
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
    
    def get_blink_config(self):
        """
        Get blink ability configuration based on level
        
        Returns:
            dict: Blink config with range and cooldown, or None if locked
        """
        blink_configs = {
            0: None,  # Locked
            1: {"range": 3, "cooldown": 15, "through_enemies": False, "name": "Blink I"},
            2: {"range": 4, "cooldown": 12, "through_enemies": False, "name": "Blink II"},
            3: {"range": 5, "cooldown": 10, "through_enemies": False, "name": "Blink III"},
            4: {"range": 5, "cooldown": 8, "through_enemies": True, "name": "Blink Master"}
        }
        
        blink_level = self.skills.get('blink', 0)
        return blink_configs.get(blink_level)
    
    def can_blink(self):
        """
        Check if blink is available (unlocked and off cooldown)
        
        Returns:
            tuple: (bool, str) - (can_blink, reason_if_not)
        """
        blink_config = self.get_blink_config()
        
        if not blink_config:
            return False, "Blink ability not unlocked"
        
        current_time = time.time()
        if current_time < self.blink_cooldown_end:
            remaining = int(self.blink_cooldown_end - current_time)
            return False, f"Blink on cooldown ({remaining}s remaining)"
        
        return True, ""
    
    def activate_blink(self, target_x, target_y, dungeon_grid, enemies):
        """
        Attempt to blink to target position
        
        Args:
            target_x, target_y: Target coordinates
            dungeon_grid: 2D array of dungeon tiles
            enemies: Dict of enemy_id -> Enemy objects
        
        Returns:
            dict: Result with success status and message
        """
        can_blink, reason = self.can_blink()
        if not can_blink:
            return {"success": False, "reason": reason}
        
        blink_config = self.get_blink_config()
        
        # Validate range (Chebyshev distance)
        distance = max(abs(target_x - self.x), abs(target_y - self.y))
        if distance > blink_config["range"]:
            return {
                "success": False,
                "reason": f"Target out of range (max {blink_config['range']} tiles)"
            }
        
        # Validate target tile is not a wall
        if not self._is_walkable_tile(target_x, target_y, dungeon_grid):
            return {"success": False, "reason": "Cannot blink into walls"}
        
        # Check for enemy occupation (unless Blink Master)
        if not blink_config["through_enemies"]:
            for enemy in enemies.values():
                if enemy.x == target_x and enemy.y == target_y:
                    return {"success": False, "reason": "Cannot blink into enemy"}
        
        # Execute blink
        old_x, old_y = self.x, self.y
        self.x = target_x
        self.y = target_y
        
        # Set cooldown
        self.blink_cooldown_end = time.time() + blink_config["cooldown"]
        
        return {
            "success": True,
            "old_position": (old_x, old_y),
            "new_position": (target_x, target_y),
            "distance": distance,
            "cooldown": blink_config["cooldown"]
        }
    
    def get_blink_cooldown_remaining(self):
        """Get remaining cooldown time in seconds"""
        current_time = time.time()
        if current_time >= self.blink_cooldown_end:
            return 0
        return int(self.blink_cooldown_end - current_time)
    
    def _is_walkable_tile(self, x, y, dungeon_grid):
        """Check if tile is walkable"""
        if not dungeon_grid:
            return True
        
        height = len(dungeon_grid)
        width = len(dungeon_grid[0]) if height > 0 else 0
        
        if x < 0 or x >= width or y < 0 or y >= height:
            return False
        
        return dungeon_grid[y][x] == 1  # 1 = floor, 0 = wall
    
    def to_dict(self):
        """Convert player to dictionary for JSON"""
        return {
            'id': self.id,
            'name': self.name,
            'user_id': self.user_id,
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
            'inventory': self.inventory,
            'gold': self.gold,
            'x': self.x,
            'y': self.y,
            'floor': self.floor,
            'active_resistance': self.active_resistance
        }
    
    def apply_resistance_potion(self, potion: Dict) -> Dict:
        """
        Apply resistance potion effect
        
        Args:
            potion: Potion item dict with element, reduction, duration
        
        Returns:
            dict: Result with success status and message
        """
        if self.active_resistance:
            old_element = self.active_resistance["element"]
            result = {
                "success": True,
                "replaced": True,
                "old_element": old_element,
                "message": f"Replaced {old_element} resistance with {potion['element']} resistance"
            }
        else:
            result = {
                "success": True,
                "replaced": False,
                "message": f"Activated {potion['element']} resistance"
            }
        
        self.active_resistance = {
            "element": potion["element"],
            "reduction": potion["reduction"],
            "turns_remaining": potion["duration"],
            "applied_turn": time.time()
        }
        
        return result
    
    def update_resistance(self) -> Tuple[bool, Optional[str]]:
        """
        Update resistance effect (call each turn)
        
        Returns:
            tuple: (expired, element) - True if resistance expired, element name if expired
        """
        if not self.active_resistance:
            return False, None
        
        self.active_resistance["turns_remaining"] -= 1
        
        if self.active_resistance["turns_remaining"] <= 0:
            expired_element = self.active_resistance["element"]
            self.active_resistance = None
            return True, expired_element
        
        return False, None
    
    def calculate_resistance_reduction(self, element: str) -> float:
        """
        Calculate damage reduction from active resistance
        
        Args:
            element: Attack element type
        
        Returns:
            float: Reduction multiplier (0.0 to 1.0)
        """
        if not self.active_resistance:
            return 0.0
        
        if self.active_resistance["element"] == element:
            return self.active_resistance["reduction"]
        
        return 0.0
