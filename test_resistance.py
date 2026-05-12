#!/usr/bin/env python
"""
Test script for resistance potion system
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from game.player import Player
import time

def test_apply_resistance_potion():
    """Test applying resistance potions"""
    print("\n=== Testing Apply Resistance Potion ===")
    
    player = Player("test_player", "TestHero")
    
    # Test applying first resistance potion
    fire_potion = {
        "element": "fire",
        "reduction": 0.40,
        "duration": 4
    }
    
    result = player.apply_resistance_potion(fire_potion)
    print(f"✓ Applied fire resistance: {result['message']}")
    assert result["success"] == True
    assert result["replaced"] == False
    assert player.active_resistance is not None
    assert player.active_resistance["element"] == "fire"
    assert player.active_resistance["reduction"] == 0.40
    assert player.active_resistance["turns_remaining"] == 4
    print(f"✓ Active resistance: {player.active_resistance['element']} (-{int(player.active_resistance['reduction']*100)}%)")
    
    # Test replacing resistance potion
    frost_potion = {
        "element": "frost",
        "reduction": 0.50,
        "duration": 3
    }
    
    result = player.apply_resistance_potion(frost_potion)
    print(f"✓ Replaced resistance: {result['message']}")
    assert result["success"] == True
    assert result["replaced"] == True
    assert result["old_element"] == "fire"
    assert player.active_resistance["element"] == "frost"
    assert player.active_resistance["reduction"] == 0.50
    assert player.active_resistance["turns_remaining"] == 3
    print(f"✓ New active resistance: {player.active_resistance['element']} (-{int(player.active_resistance['reduction']*100)}%)")

def test_update_resistance():
    """Test resistance turn countdown and expiration"""
    print("\n=== Testing Update Resistance ===")
    
    player = Player("test_player", "TestHero")
    
    # Apply resistance with 3 turns
    potion = {
        "element": "lightning",
        "reduction": 0.35,
        "duration": 3
    }
    player.apply_resistance_potion(potion)
    print(f"✓ Applied lightning resistance for 3 turns")
    
    # Update turn 1
    expired, element = player.update_resistance()
    assert expired == False
    assert element is None
    assert player.active_resistance["turns_remaining"] == 2
    print(f"✓ Turn 1: {player.active_resistance['turns_remaining']} turns remaining")
    
    # Update turn 2
    expired, element = player.update_resistance()
    assert expired == False
    assert element is None
    assert player.active_resistance["turns_remaining"] == 1
    print(f"✓ Turn 2: {player.active_resistance['turns_remaining']} turn remaining")
    
    # Update turn 3 - should expire
    expired, element = player.update_resistance()
    assert expired == True
    assert element == "lightning"
    assert player.active_resistance is None
    print(f"✓ Turn 3: Resistance expired ({element})")
    
    # Update with no active resistance
    expired, element = player.update_resistance()
    assert expired == False
    assert element is None
    print(f"✓ No active resistance: update returns (False, None)")

def test_calculate_resistance_reduction():
    """Test damage reduction calculation"""
    print("\n=== Testing Calculate Resistance Reduction ===")
    
    player = Player("test_player", "TestHero")
    
    # Test with no active resistance
    reduction = player.calculate_resistance_reduction("fire")
    assert reduction == 0.0
    print(f"✓ No active resistance: reduction = {reduction}")
    
    # Apply fire resistance
    fire_potion = {
        "element": "fire",
        "reduction": 0.45,
        "duration": 5
    }
    player.apply_resistance_potion(fire_potion)
    
    # Test matching element
    reduction = player.calculate_resistance_reduction("fire")
    assert reduction == 0.45
    print(f"✓ Fire resistance vs fire attack: reduction = {reduction} (45%)")
    
    # Test non-matching element
    reduction = player.calculate_resistance_reduction("frost")
    assert reduction == 0.0
    print(f"✓ Fire resistance vs frost attack: reduction = {reduction} (0%)")
    
    # Test physical (no element)
    reduction = player.calculate_resistance_reduction("physical")
    assert reduction == 0.0
    print(f"✓ Fire resistance vs physical attack: reduction = {reduction} (0%)")

def test_resistance_data_structure():
    """Test resistance dict structure"""
    print("\n=== Testing Resistance Data Structure ===")
    
    player = Player("test_player", "TestHero")
    
    potion = {
        "element": "shadow",
        "reduction": 0.30,
        "duration": 5
    }
    
    player.apply_resistance_potion(potion)
    
    # Verify structure
    assert "element" in player.active_resistance
    assert "reduction" in player.active_resistance
    assert "turns_remaining" in player.active_resistance
    assert "applied_turn" in player.active_resistance
    print(f"✓ Resistance dict has all required fields")
    
    # Verify types
    assert isinstance(player.active_resistance["element"], str)
    assert isinstance(player.active_resistance["reduction"], float)
    assert isinstance(player.active_resistance["turns_remaining"], int)
    assert isinstance(player.active_resistance["applied_turn"], float)
    print(f"✓ All fields have correct types")
    
    # Verify values
    assert player.active_resistance["element"] == "shadow"
    assert player.active_resistance["reduction"] == 0.30
    assert player.active_resistance["turns_remaining"] == 5
    assert player.active_resistance["applied_turn"] > 0
    print(f"✓ All values stored correctly")

def test_multiple_elements():
    """Test all 7 resistance elements"""
    print("\n=== Testing All Resistance Elements ===")
    
    player = Player("test_player", "TestHero")
    
    elements = ["fire", "frost", "lightning", "poison", "shadow", "holy", "void"]
    
    for element in elements:
        potion = {
            "element": element,
            "reduction": 0.40,
            "duration": 3
        }
        player.apply_resistance_potion(potion)
        
        # Test matching element
        reduction = player.calculate_resistance_reduction(element)
        assert reduction == 0.40
        print(f"✓ {element.capitalize()} resistance: {int(reduction*100)}% reduction")

def test_edge_cases():
    """Test edge cases"""
    print("\n=== Testing Edge Cases ===")
    
    player = Player("test_player", "TestHero")
    
    # Test minimum reduction (30%)
    min_potion = {
        "element": "fire",
        "reduction": 0.30,
        "duration": 3
    }
    player.apply_resistance_potion(min_potion)
    assert player.active_resistance["reduction"] == 0.30
    print(f"✓ Minimum reduction (30%): {player.active_resistance['reduction']}")
    
    # Test maximum reduction (50%)
    max_potion = {
        "element": "frost",
        "reduction": 0.50,
        "duration": 5
    }
    player.apply_resistance_potion(max_potion)
    assert player.active_resistance["reduction"] == 0.50
    print(f"✓ Maximum reduction (50%): {player.active_resistance['reduction']}")
    
    # Test minimum duration (3 turns)
    min_duration_potion = {
        "element": "lightning",
        "reduction": 0.40,
        "duration": 3
    }
    player.apply_resistance_potion(min_duration_potion)
    assert player.active_resistance["turns_remaining"] == 3
    print(f"✓ Minimum duration (3 turns): {player.active_resistance['turns_remaining']}")
    
    # Test maximum duration (5 turns)
    max_duration_potion = {
        "element": "poison",
        "reduction": 0.40,
        "duration": 5
    }
    player.apply_resistance_potion(max_duration_potion)
    assert player.active_resistance["turns_remaining"] == 5
    print(f"✓ Maximum duration (5 turns): {player.active_resistance['turns_remaining']}")

if __name__ == '__main__':
    print("=" * 60)
    print("Resistance Potion System Test")
    print("=" * 60)
    
    try:
        test_apply_resistance_potion()
        test_update_resistance()
        test_calculate_resistance_reduction()
        test_resistance_data_structure()
        test_multiple_elements()
        test_edge_cases()
        
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
