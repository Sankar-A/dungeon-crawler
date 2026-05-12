"""
Test script to verify boss ability configurations for Task 3.1
"""
from game.lore_data import RARE_BOSSES

def test_boss_abilities_part1():
    """Test that the first 4 bosses have complete ability configurations"""
    
    # Boss IDs to test
    boss_ids = ["shadow_king", "storm_titan", "lich_king", "phoenix_queen"]
    
    for boss_id in boss_ids:
        boss = next((b for b in RARE_BOSSES if b["id"] == boss_id), None)
        assert boss is not None, f"Boss {boss_id} not found"
        
        print(f"\n✓ Testing {boss['name']} ({boss_id})...")
        
        # Check abilities is a list of dicts, not strings
        assert isinstance(boss["abilities"], list), f"{boss_id}: abilities should be a list"
        assert len(boss["abilities"]) > 0, f"{boss_id}: should have at least one ability"
        
        for ability in boss["abilities"]:
            assert isinstance(ability, dict), f"{boss_id}: ability should be a dict, not string"
            
            # Check required fields
            assert "name" in ability, f"{boss_id}: ability missing 'name'"
            assert "telegraph_turns" in ability, f"{boss_id}: ability missing 'telegraph_turns'"
            assert "attack_zone" in ability, f"{boss_id}: ability missing 'attack_zone'"
            assert "element" in ability, f"{boss_id}: ability missing 'element'"
            assert "damage_multiplier" in ability, f"{boss_id}: ability missing 'damage_multiplier'"
            assert "special_effects" in ability, f"{boss_id}: ability missing 'special_effects'"
            
            # Check attack_zone structure
            assert isinstance(ability["attack_zone"], dict), f"{boss_id}: attack_zone should be dict"
            assert "type" in ability["attack_zone"], f"{boss_id}: attack_zone missing 'type'"
            
            print(f"  ✓ {ability['name']}: telegraph={ability['telegraph_turns']}, zone={ability['attack_zone']['type']}, element={ability['element']}, multiplier={ability['damage_multiplier']}")
        
        # Check attack_pattern
        assert "attack_pattern" in boss, f"{boss_id}: missing 'attack_pattern'"
        assert "type" in boss["attack_pattern"], f"{boss_id}: attack_pattern missing 'type'"
        assert "sequence" in boss["attack_pattern"], f"{boss_id}: attack_pattern missing 'sequence'"
        
        print(f"  ✓ Attack pattern: {boss['attack_pattern']['type']} - {boss['attack_pattern']['sequence']}")

def test_specific_boss_configs():
    """Test specific requirements from Task 3.1"""
    
    print("\n\n=== Testing Specific Boss Configurations ===")
    
    # Test Shadow King
    shadow_king = next(b for b in RARE_BOSSES if b["id"] == "shadow_king")
    assert shadow_king["abilities"][0]["name"] == "shadow_strike"
    assert shadow_king["abilities"][0]["telegraph_turns"] == 0
    assert shadow_king["abilities"][0]["attack_zone"]["type"] == "none"
    assert shadow_king["abilities"][0]["element"] == "shadow"
    assert shadow_king["abilities"][0]["damage_multiplier"] == 1.5
    assert shadow_king["abilities"][0]["special_effects"]["armor_penetration"] == 0.5
    
    assert shadow_king["abilities"][1]["name"] == "darkness_aura"
    assert shadow_king["abilities"][1]["telegraph_turns"] == 1
    assert shadow_king["abilities"][1]["attack_zone"]["type"] == "circle"
    assert shadow_king["abilities"][1]["attack_zone"]["radius"] == 3
    assert shadow_king["abilities"][1]["special_effects"]["blind"] == True
    print("✓ Shadow King configuration correct")
    
    # Test Storm Titan
    storm_titan = next(b for b in RARE_BOSSES if b["id"] == "storm_titan")
    assert len(storm_titan["abilities"]) == 3
    assert storm_titan["abilities"][0]["name"] == "lightning_bolt"
    assert storm_titan["abilities"][0]["telegraph_turns"] == 1
    assert storm_titan["abilities"][1]["name"] == "chain_lightning"
    assert storm_titan["abilities"][1]["attack_zone"]["type"] == "line"
    assert storm_titan["abilities"][1]["attack_zone"]["range"] == 5
    assert storm_titan["abilities"][1]["attack_zone"]["width"] == 1
    assert storm_titan["abilities"][2]["name"] == "thunder_clap"
    assert storm_titan["abilities"][2]["special_effects"]["stun"] == True
    print("✓ Storm Titan configuration correct")
    
    # Test Lich King
    lich_king = next(b for b in RARE_BOSSES if b["id"] == "lich_king")
    assert lich_king["abilities"][0]["name"] == "frost_nova"
    assert lich_king["abilities"][0]["element"] == "frost"
    assert lich_king["abilities"][0]["special_effects"]["freeze"] == True
    assert lich_king["abilities"][1]["name"] == "death_coil"
    assert lich_king["abilities"][1]["special_effects"]["heal_boss"] == 0.5
    assert lich_king["abilities"][2]["name"] == "raise_dead"
    assert lich_king["abilities"][2]["damage_multiplier"] == 0
    assert lich_king["abilities"][2]["special_effects"]["summon"] == True
    print("✓ Lich King configuration correct")
    
    # Test Phoenix Queen
    phoenix_queen = next(b for b in RARE_BOSSES if b["id"] == "phoenix_queen")
    assert phoenix_queen["abilities"][0]["name"] == "flame_burst"
    assert phoenix_queen["abilities"][0]["attack_zone"]["type"] == "cone"
    assert phoenix_queen["abilities"][0]["attack_zone"]["range"] == 3
    assert phoenix_queen["abilities"][0]["special_effects"]["burn"] == True
    assert phoenix_queen["abilities"][1]["name"] == "inferno"
    assert phoenix_queen["abilities"][1]["telegraph_turns"] == 2
    assert phoenix_queen["abilities"][1]["attack_zone"]["radius"] == 5
    assert phoenix_queen["abilities"][1]["damage_multiplier"] == 2.5
    assert phoenix_queen["abilities"][2]["name"] == "rebirth"
    assert phoenix_queen["abilities"][2]["special_effects"]["heal_on_low_hp"] == 0.3
    print("✓ Phoenix Queen configuration correct")

if __name__ == "__main__":
    print("=== Testing Boss Ability Configurations (Task 3.1) ===")
    test_boss_abilities_part1()
    test_specific_boss_configs()
    print("\n\n✅ All tests passed! Boss configurations are correct.")
