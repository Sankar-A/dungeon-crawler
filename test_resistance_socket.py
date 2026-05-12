#!/usr/bin/env python
"""
Test script for resistance potion socket events
"""
import sys
sys.path.insert(0, '.')

from game.player import Player

def test_use_resistance_potion_handler():
    """Test the use_resistance_potion socket event handler logic"""
    print("\n=== Testing Use Resistance Potion Handler Logic ===")
    
    player = Player("test_player", "TestHero")
    
    # Add resistance potions to inventory
    fire_potion = {
        "type": "consumable",
        "subtype": "resistance_potion",
        "name": "Fire Resistance Potion",
        "element": "fire",
        "reduction": 0.40,
        "duration": 4,
        "rarity": "uncommon"
    }
    
    frost_potion = {
        "type": "consumable",
        "subtype": "resistance_potion",
        "name": "Frost Resistance Potion",
        "element": "frost",
        "reduction": 0.50,
        "duration": 3,
        "rarity": "rare"
    }
    
    player.inventory.append(fire_potion)
    player.inventory.append(frost_potion)
    
    print(f"✓ Added 2 resistance potions to inventory")
    print(f"  Inventory size: {len(player.inventory)}")
    
    # Test using first potion (fire)
    potion_index = 0
    potion = player.inventory[potion_index]
    
    # Validate it's a resistance potion
    assert potion.get('type') == 'consumable'
    assert potion.get('subtype') == 'resistance_potion'
    print(f"✓ Validated potion at index {potion_index} is a resistance potion")
    
    # Apply resistance
    result = player.apply_resistance_potion(potion)
    assert result.get('success') == True
    assert result.get('replaced') == False
    print(f"✓ Applied {potion['element']} resistance: {result.get('message')}")
    
    # Remove from inventory
    player.inventory.pop(potion_index)
    print(f"✓ Removed potion from inventory")
    print(f"  Inventory size: {len(player.inventory)}")
    
    # Verify active resistance
    assert player.active_resistance is not None
    assert player.active_resistance['element'] == 'fire'
    assert player.active_resistance['reduction'] == 0.40
    assert player.active_resistance['turns_remaining'] == 4
    print(f"✓ Active resistance: {player.active_resistance['element']} (-{int(player.active_resistance['reduction']*100)}%)")
    
    # Test using second potion (frost) - should replace fire
    potion_index = 0  # Now frost is at index 0
    potion = player.inventory[potion_index]
    
    result = player.apply_resistance_potion(potion)
    assert result.get('success') == True
    assert result.get('replaced') == True
    assert result.get('old_element') == 'fire'
    print(f"✓ Replaced resistance: {result.get('message')}")
    
    player.inventory.pop(potion_index)
    print(f"✓ Removed potion from inventory")
    print(f"  Inventory size: {len(player.inventory)}")
    
    # Verify new active resistance
    assert player.active_resistance['element'] == 'frost'
    assert player.active_resistance['reduction'] == 0.50
    print(f"✓ New active resistance: {player.active_resistance['element']} (-{int(player.active_resistance['reduction']*100)}%)")

def test_resistance_expiration():
    """Test resistance expiration during turn updates"""
    print("\n=== Testing Resistance Expiration ===")
    
    player = Player("test_player", "TestHero")
    
    # Apply resistance with 2 turns duration
    potion = {
        "element": "lightning",
        "reduction": 0.35,
        "duration": 2
    }
    
    player.apply_resistance_potion(potion)
    print(f"✓ Applied lightning resistance for 2 turns")
    
    # Turn 1
    expired, expired_element = player.update_resistance()
    assert expired == False
    assert expired_element is None
    assert player.active_resistance['turns_remaining'] == 1
    print(f"✓ Turn 1: 1 turn remaining, not expired")
    
    # Turn 2 - should expire
    expired, expired_element = player.update_resistance()
    assert expired == True
    assert expired_element == 'lightning'
    assert player.active_resistance is None
    print(f"✓ Turn 2: Resistance expired (element: {expired_element})")
    
    # Turn 3 - no active resistance
    expired, expired_element = player.update_resistance()
    assert expired == False
    assert expired_element is None
    print(f"✓ Turn 3: No active resistance")

def test_player_to_dict_includes_resistance():
    """Test that player.to_dict() includes active_resistance"""
    print("\n=== Testing Player to_dict() Includes Resistance ===")
    
    player = Player("test_player", "TestHero")
    
    # Test with no active resistance
    player_dict = player.to_dict()
    assert 'active_resistance' in player_dict
    assert player_dict['active_resistance'] is None
    print(f"✓ Player dict includes active_resistance: None")
    
    # Test with active resistance
    potion = {
        "element": "shadow",
        "reduction": 0.45,
        "duration": 5
    }
    player.apply_resistance_potion(potion)
    
    player_dict = player.to_dict()
    assert 'active_resistance' in player_dict
    assert player_dict['active_resistance'] is not None
    assert player_dict['active_resistance']['element'] == 'shadow'
    assert player_dict['active_resistance']['reduction'] == 0.45
    assert player_dict['active_resistance']['turns_remaining'] == 5
    print(f"✓ Player dict includes active_resistance: {player_dict['active_resistance']['element']}")

def test_invalid_potion_validation():
    """Test validation of invalid potions"""
    print("\n=== Testing Invalid Potion Validation ===")
    
    player = Player("test_player", "TestHero")
    
    # Add non-resistance items to inventory
    weapon = {
        "type": "weapon",
        "name": "Iron Sword",
        "damage": 10
    }
    
    health_potion = {
        "type": "consumable",
        "subtype": "health_potion",
        "name": "Health Potion",
        "heal": 50
    }
    
    player.inventory.append(weapon)
    player.inventory.append(health_potion)
    
    # Test weapon (wrong type)
    potion = player.inventory[0]
    assert potion.get('type') != 'consumable' or potion.get('subtype') != 'resistance_potion'
    print(f"✓ Weapon correctly identified as not a resistance potion")
    
    # Test health potion (wrong subtype)
    potion = player.inventory[1]
    assert potion.get('type') == 'consumable'
    assert potion.get('subtype') != 'resistance_potion'
    print(f"✓ Health potion correctly identified as not a resistance potion")

if __name__ == '__main__':
    print("=" * 60)
    print("Resistance Potion Socket Event Handler Test")
    print("=" * 60)
    
    try:
        test_use_resistance_potion_handler()
        test_resistance_expiration()
        test_player_to_dict_includes_resistance()
        test_invalid_potion_validation()
        
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
