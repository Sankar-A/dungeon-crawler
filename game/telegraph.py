"""
Telegraph phase management for boss special attacks
"""
import time


class TelegraphManager:
    """Manages telegraph phases for boss attacks"""
    
    def __init__(self):
        self.active_telegraphs = {}  # enemy_id -> telegraph_state
    
    def start_telegraph(self, enemy_id, ability_config, enemy):
        """
        Start a telegraph phase for a boss ability
        
        Args:
            enemy_id: Unique enemy identifier
            ability_config: Ability dict with telegraph_turns
            enemy: Enemy object
        
        Returns:
            dict: Telegraph state for client synchronization
        """
        telegraph_turns = ability_config.get("telegraph_turns", 0)
        
        if telegraph_turns <= 0:
            return None  # No telegraph for this ability
        
        telegraph_state = {
            "enemy_id": enemy_id,
            "ability": ability_config,
            "turns_remaining": telegraph_turns,
            "started_turn": time.time(),
            "boss_name": enemy.name,
            "boss_position": (enemy.x, enemy.y),
            "boss_facing": enemy.facing_direction
        }
        
        self.active_telegraphs[enemy_id] = telegraph_state
        
        # Update enemy state
        enemy.telegraph_active = True
        enemy.telegraph_ability = ability_config
        enemy.telegraph_turns_remaining = telegraph_turns
        
        return telegraph_state
    
    def update_telegraph(self, enemy_id):
        """
        Decrement telegraph counter (called each turn)
        
        Args:
            enemy_id: Unique enemy identifier
        
        Returns:
            bool: True if telegraph should execute, False if still counting
        """
        if enemy_id not in self.active_telegraphs:
            return False
        
        telegraph = self.active_telegraphs[enemy_id]
        telegraph["turns_remaining"] -= 1
        
        if telegraph["turns_remaining"] <= 0:
            return True  # Ready to execute
        
        return False
    
    def execute_telegraph(self, enemy_id):
        """
        Execute the telegraphed attack and cleanup state
        
        Args:
            enemy_id: Unique enemy identifier
        
        Returns:
            dict: Ability config to execute, or None if not found
        """
        if enemy_id not in self.active_telegraphs:
            return None
        
        telegraph = self.active_telegraphs[enemy_id]
        ability = telegraph["ability"]
        
        # Clean up telegraph state
        del self.active_telegraphs[enemy_id]
        
        return ability
    
    def cancel_telegraph(self, enemy_id):
        """
        Cancel telegraph (e.g., boss defeated during telegraph phase)
        
        Args:
            enemy_id: Unique enemy identifier
        """
        if enemy_id in self.active_telegraphs:
            del self.active_telegraphs[enemy_id]
    
    def get_telegraph_state(self, enemy_id):
        """
        Get current telegraph state for an enemy
        
        Args:
            enemy_id: Unique enemy identifier
        
        Returns:
            dict: Telegraph state dict, or None if no active telegraph
        """
        return self.active_telegraphs.get(enemy_id)


# Global telegraph manager instance
telegraph_manager = TelegraphManager()
