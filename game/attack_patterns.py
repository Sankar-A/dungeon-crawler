"""
Boss attack pattern management
"""
import random


class AttackPatternManager:
    """Manages boss attack patterns (predictable vs random)"""
    
    def __init__(self):
        self.pattern_states = {}  # enemy_id -> pattern_state
    
    def initialize_pattern(self, enemy_id, boss_data):
        """
        Initialize attack pattern for a boss
        
        Args:
            enemy_id: Unique enemy identifier
            boss_data: Boss configuration from lore_data
        """
        pattern_config = boss_data.get("attack_pattern", {})
        pattern_type = pattern_config.get("type", "predictable")
        
        if pattern_type == "predictable":
            sequence = pattern_config.get("sequence", [])
            self.pattern_states[enemy_id] = {
                "type": "predictable",
                "sequence": sequence,
                "current_index": 0
            }
        else:  # random
            abilities = [a["name"] for a in boss_data.get("abilities", [])]
            self.pattern_states[enemy_id] = {
                "type": "random",
                "abilities": abilities
            }
    
    def get_next_ability(self, enemy_id, boss_data):
        """
        Get the next ability to use based on pattern
        
        Returns:
            dict: Ability configuration
        """
        if enemy_id not in self.pattern_states:
            self.initialize_pattern(enemy_id, boss_data)
        
        pattern_state = self.pattern_states[enemy_id]
        abilities = boss_data.get("abilities", [])
        
        if pattern_state["type"] == "predictable":
            # Get next in sequence
            sequence = pattern_state["sequence"]
            current_index = pattern_state["current_index"]
            
            if not sequence:
                # Fallback to random if no sequence defined
                return random.choice(abilities)
            
            ability_name = sequence[current_index]
            
            # Advance index (wrap around)
            pattern_state["current_index"] = (current_index + 1) % len(sequence)
            
            # Find ability config by name
            ability = next((a for a in abilities if a["name"] == ability_name), None)
            return ability if ability else random.choice(abilities)
        
        else:  # random
            return random.choice(abilities)
    
    def reset_pattern(self, enemy_id):
        """Reset pattern to beginning (e.g., boss phase change)"""
        if enemy_id in self.pattern_states:
            if self.pattern_states[enemy_id]["type"] == "predictable":
                self.pattern_states[enemy_id]["current_index"] = 0
    
    def cleanup_pattern(self, enemy_id):
        """Remove pattern state (boss defeated)"""
        if enemy_id in self.pattern_states:
            del self.pattern_states[enemy_id]


# Global pattern manager instance
pattern_manager = AttackPatternManager()
