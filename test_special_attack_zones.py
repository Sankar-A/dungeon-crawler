"""
Test script for execute_special_attack_with_zones function
"""
import sys
sys.path.insert(0, '.')

from game.combat import Enemy, execute_special_attack_with_zones
from game.player import Player
from game.lore_data import RARE_BOSSES

def test_attack_avoided():
    """Test that player outside zone avoids attack"""
    print("\n=== Test 1: Attack Avoided (Player Outside Zone) ===")
    
    # Create boss at position (5, 5)
    boss_data = RARE_BOSSES[0]  # Shadow King
    boss = Enemy(10, 5, 5, is_boss=True, boss_data=boss_data)
    boss.facing_direction = "down"
    
    # Create player far away at (10, 10)
    player = Player("test_player", "TestPlayer")
    player.x = 10
    player.y = 10
    player.hp = 100
    player.max_hp = 100
    
    # Create ability with circle zone (radius 3)
    ability = {
        'name': 'darkness_aura',
        'attack_zone': {
            'type': 'circle',
            'radius': 3
        },
        'damage_multiplier': 1.0,
        'special_effects': {}
    }
    
    result = execute_special_attack_with_zones(boss, player, ability)
    
    print(f"Avoided: {result['avoided']}")
    print(f"Damage: {result['damage']}")
    print(f"Description: {result['description']}")
    
    assert result['avoided'] == True, "Attack should be avoided"
    assert result['damage'] == 0, "Damage should be 0 when avoided"
    print("✓ Test passed!")


def test_attack_hits():
    """Test that player inside zone takes damage"""
    print("\n=== Test 2: Attack Hits (Player Inside Zone) ===")
    
    # Create boss at position (5, 5)
    boss_data = RARE_BOSSES[0]  # Shadow King
    boss = Enemy(10, 5, 5, is_boss=True, boss_data=boss_data)
    boss.facing_direction = "down"
    
    # Create player nearby at (6, 6)
    player = Player("test_player", "TestPlayer")
    player.x = 6
    player.y = 6
    player.hp = 100
    player.max_hp = 100
    
    # Create ability with circle zone (radius 3)
    ability = {
        'name': 'darkness_aura',
        'attack_zone': {
            'type': 'circle',
            'radius': 3
        },
        'damage_multiplier': 1.0,
        'special_effects': {
            'blind': True
        }
    }
    
    result = execute_special_attack_with_zones(boss, player, ability)
    
    print(f"Avoided: {result['avoided']}")
    print(f"Damage: {result['damage']}")
    print(f"Status Effects: {result['status_effects']}")
    print(f"Description: {result['description']}")
    
    assert result['avoided'] == False, "Attack should hit"
    assert result['damage'] > 0, "Damage should be > 0 when hit"
    assert 'blinded' in result['status_effects'], "Should apply blind effect"
    print("✓ Test passed!")


def test_resistance_reduction():
    """Test that resistance reduces damage"""
    print("\n=== Test 3: Resistance Reduction ===")
    
    # Create boss
    boss_data = RARE_BOSSES[0]  # Shadow King
    boss = Enemy(10, 5, 5, is_boss=True, boss_data=boss_data)
    boss.facing_direction = "down"
    
    # Create player with active shadow resistance
    player = Player("test_player", "TestPlayer")
    player.x = 5
    player.y = 5
    player.hp = 100
    player.max_hp = 100
    
    # Apply shadow resistance potion (40% reduction)
    player.active_resistance = {
        'element': 'shadow',
        'reduction': 0.40,
        'turns_remaining': 3
    }
    
    # Shadow strike ability (shadow element)
    ability = {
        'name': 'shadow_strike',
        'attack_zone': {
            'type': 'none'
        },
        'damage_multiplier': 1.5,
        'special_effects': {
            'armor_penetration': 0.5
        }
    }
    
    result = execute_special_attack_with_zones(boss, player, ability)
    
    print(f"Resisted: {result['resisted']}")
    print(f"Resistance Reduction: {result['resistance_reduction']}")
    print(f"Damage: {result['damage']}")
    print(f"Description: {result['description']}")
    
    assert result['resisted'] == True, "Should be resisted"
    assert result['resistance_reduction'] == 0.40, "Should have 40% reduction"
    print("✓ Test passed!")


def test_armor_penetration():
    """Test that armor penetration works correctly"""
    print("\n=== Test 4: Armor Penetration ===")
    
    # Create boss
    boss_data = RARE_BOSSES[0]  # Shadow King
    boss = Enemy(10, 5, 5, is_boss=True, boss_data=boss_data)
    
    # Create player with high defense
    player = Player("test_player", "TestPlayer")
    player.x = 5
    player.y = 5
    player.hp = 100
    player.max_hp = 100
    player.vitality = 50  # High defense
    
    # Ability with 50% armor penetration
    ability = {
        'name': 'shadow_strike',
        'attack_zone': {
            'type': 'none'
        },
        'damage_multiplier': 1.5,
        'special_effects': {
            'armor_penetration': 0.5
        }
    }
    
    result = execute_special_attack_with_zones(boss, player, ability)
    
    print(f"Damage: {result['damage']}")
    print(f"Description: {result['description']}")
    
    assert result['damage'] > 0, "Should deal damage"
    print("✓ Test passed!")


def test_heal_boss():
    """Test that heal_boss special effect works"""
    print("\n=== Test 5: Heal Boss Effect ===")
    
    # Create boss with reduced HP
    boss_data = RARE_BOSSES[2]  # Lich King
    boss = Enemy(20, 5, 5, is_boss=True, boss_data=boss_data)
    boss.hp = boss.max_hp // 2  # Half health
    initial_hp = boss.hp
    
    # Create player
    player = Player("test_player", "TestPlayer")
    player.x = 5
    player.y = 5
    player.hp = 100
    player.max_hp = 100
    
    # Death coil ability (heals boss)
    ability = {
        'name': 'death_coil',
        'attack_zone': {
            'type': 'none'
        },
        'damage_multiplier': 1.2,
        'special_effects': {
            'heal_boss': 0.5
        }
    }
    
    result = execute_special_attack_with_zones(boss, player, ability)
    
    print(f"Damage to player: {result['damage']}")
    print(f"Boss healed: {result.get('enemy_healed', 0)}")
    print(f"Boss HP: {initial_hp} -> {boss.hp}")
    
    assert 'enemy_healed' in result, "Should heal boss"
    assert boss.hp > initial_hp, "Boss HP should increase"
    print("✓ Test passed!")


if __name__ == '__main__':
    print("Testing execute_special_attack_with_zones function...")
    
    try:
        test_attack_avoided()
        test_attack_hits()
        test_resistance_reduction()
        test_armor_penetration()
        test_heal_boss()
        
        print("\n" + "="*50)
        print("✓ All tests passed!")
        print("="*50)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
