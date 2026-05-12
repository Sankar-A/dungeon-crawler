"""
Test script for blink ability functionality
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from game.player import Player
import time

def test_blink_config():
    print("\n=== Testing Blink Config ===")
    
    player = Player("test_player", "TestHero")
    
    # Test locked state
    config = player.get_blink_config()
    assert config is None
    print("✓ Blink locked (level 0): config = None")
    
    # Test Blink I
    player.skills['blink'] = 1
    config = player.get_blink_config()
    assert config is not None
    assert config["range"] == 3
    assert config["cooldown"] == 15
    assert config["through_enemies"] == False
    assert config["name"] == "Blink I"
    print(f"✓ Blink I: range={config['range']}, cooldown={config['cooldown']}s")
    
    # Test Blink II
    player.skills['blink'] = 2
    config = player.get_blink_config()
    assert config["range"] == 4
    assert config["cooldown"] == 12
    assert config["through_enemies"] == False
    assert config["name"] == "Blink II"
    print(f"✓ Blink II: range={config['range']}, cooldown={config['cooldown']}s")
    
    # Test Blink III
    player.skills['blink'] = 3
    config = player.get_blink_config()
    assert config["range"] == 5
    assert config["cooldown"] == 10
    assert config["through_enemies"] == False
    assert config["name"] == "Blink III"
    print(f"✓ Blink III: range={config['range']}, cooldown={config['cooldown']}s")
    
    # Test Blink Master
    player.skills['blink'] = 4
    config = player.get_blink_config()
    assert config["range"] == 5
    assert config["cooldown"] == 8
    assert config["through_enemies"] == True
    assert config["name"] == "Blink Master"
    print(f"✓ Blink Master: range={config['range']}, cooldown={config['cooldown']}s, through_enemies={config['through_enemies']}")

def test_can_blink():
    print("\n=== Testing Can Blink ===")
    
    player = Player("test_player", "TestHero")
    
    # Test locked
    can_blink, reason = player.can_blink()
    assert can_blink == False
    assert "not unlocked" in reason
    print(f"✓ Locked: can_blink={can_blink}, reason='{reason}'")
    
    # Test unlocked, no cooldown
    player.skills['blink'] = 1
    can_blink, reason = player.can_blink()
    assert can_blink == True
    assert reason == ""
    print(f"✓ Unlocked, ready: can_blink={can_blink}")
    
    # Test on cooldown
    player.blink_cooldown_end = time.time() + 10
    can_blink, reason = player.can_blink()
    assert can_blink == False
    assert "cooldown" in reason
    print(f"✓ On cooldown: can_blink={can_blink}, reason='{reason}'")
    
    # Test cooldown expired
    player.blink_cooldown_end = time.time() - 1
    can_blink, reason = player.can_blink()
    assert can_blink == True
    assert reason == ""
    print(f"✓ Cooldown expired: can_blink={can_blink}")

def test_activate_blink():
    print("\n=== Testing Activate Blink ===")
    
    player = Player("test_player", "TestHero")
    player.x = 5
    player.y = 5
    player.skills['blink'] = 1  # Blink I: range 3
    
    # Create simple dungeon grid (10x10, all walkable)
    dungeon_grid = [[1 for _ in range(10)] for _ in range(10)]
    enemies = {}
    
    # Test successful blink
    result = player.activate_blink(7, 6, dungeon_grid, enemies)
    assert result["success"] == True
    assert player.x == 7
    assert player.y == 6
    assert result["old_position"] == (5, 5)
    assert result["new_position"] == (7, 6)
    assert result["distance"] == 2  # Chebyshev distance: max(|7-5|, |6-5|) = 2
    print(f"✓ Successful blink: {result['old_position']} -> {result['new_position']}, distance={result['distance']}")
    
    # Test out of range
    player.x = 5
    player.y = 5
    player.blink_cooldown_end = 0  # Reset cooldown
    result = player.activate_blink(10, 10, dungeon_grid, enemies)
    assert result["success"] == False
    assert "out of range" in result["reason"]
    assert player.x == 5  # Position unchanged
    assert player.y == 5
    print(f"✓ Out of range: {result['reason']}")
    
    # Test wall collision
    dungeon_grid[6][7] = 0  # Make (7, 6) a wall
    player.blink_cooldown_end = 0
    result = player.activate_blink(7, 6, dungeon_grid, enemies)
    assert result["success"] == False
    assert "wall" in result["reason"]
    print(f"✓ Wall collision: {result['reason']}")
    
    # Test enemy collision (without Blink Master)
    dungeon_grid[6][7] = 1  # Make walkable again
    class MockEnemy:
        def __init__(self, x, y):
            self.x = x
            self.y = y
    
    enemies["enemy1"] = MockEnemy(7, 6)
    player.blink_cooldown_end = 0
    result = player.activate_blink(7, 6, dungeon_grid, enemies)
    assert result["success"] == False
    assert "enemy" in result["reason"]
    print(f"✓ Enemy collision: {result['reason']}")
    
    # Test Blink Master through enemies
    player.skills['blink'] = 4  # Blink Master
    player.blink_cooldown_end = 0
    result = player.activate_blink(7, 6, dungeon_grid, enemies)
    assert result["success"] == True
    assert player.x == 7
    assert player.y == 6
    print(f"✓ Blink Master through enemy: success")

def test_chebyshev_distance():
    print("\n=== Testing Chebyshev Distance ===")
    
    player = Player("test_player", "TestHero")
    player.x = 5
    player.y = 5
    player.skills['blink'] = 1  # Range 3
    
    dungeon_grid = [[1 for _ in range(10)] for _ in range(10)]
    enemies = {}
    
    # Test diagonal (Chebyshev distance = max of x and y differences)
    # From (5,5) to (8,8): max(|8-5|, |8-5|) = 3
    result = player.activate_blink(8, 8, dungeon_grid, enemies)
    assert result["success"] == True
    assert result["distance"] == 3
    print(f"✓ Diagonal blink (5,5) -> (8,8): distance={result['distance']}")
    
    # Test horizontal
    player.x = 5
    player.y = 5
    player.blink_cooldown_end = 0
    result = player.activate_blink(8, 5, dungeon_grid, enemies)
    assert result["success"] == True
    assert result["distance"] == 3
    print(f"✓ Horizontal blink (5,5) -> (8,5): distance={result['distance']}")
    
    # Test vertical
    player.x = 5
    player.y = 5
    player.blink_cooldown_end = 0
    result = player.activate_blink(5, 8, dungeon_grid, enemies)
    assert result["success"] == True
    assert result["distance"] == 3
    print(f"✓ Vertical blink (5,5) -> (5,8): distance={result['distance']}")

def test_cooldown_tracking():
    print("\n=== Testing Cooldown Tracking ===")
    
    player = Player("test_player", "TestHero")
    player.x = 5
    player.y = 5
    player.skills['blink'] = 1  # 15s cooldown
    
    dungeon_grid = [[1 for _ in range(10)] for _ in range(10)]
    enemies = {}
    
    # Activate blink
    result = player.activate_blink(7, 7, dungeon_grid, enemies)
    assert result["success"] == True
    assert result["cooldown"] == 15
    
    # Check cooldown is set
    remaining = player.get_blink_cooldown_remaining()
    assert remaining > 0
    assert remaining <= 15
    print(f"✓ Cooldown set: {remaining}s remaining")
    
    # Try to blink again (should fail)
    result = player.activate_blink(8, 8, dungeon_grid, enemies)
    assert result["success"] == False
    assert "cooldown" in result["reason"]
    print(f"✓ Blink blocked by cooldown: {result['reason']}")
    
    # Simulate cooldown expiry
    player.blink_cooldown_end = time.time() - 1
    remaining = player.get_blink_cooldown_remaining()
    assert remaining == 0
    print(f"✓ Cooldown expired: {remaining}s remaining")
    
    # Should be able to blink again
    can_blink, reason = player.can_blink()
    assert can_blink == True
    print(f"✓ Can blink again after cooldown")

def test_upgrade_skill():
    print("\n=== Testing Upgrade Skill ===")
    
    player = Player("test_player", "TestHero")
    player.skill_points = 5
    
    # Test sequential unlock
    assert player.skills['blink'] == 0
    
    # Upgrade to Blink I
    success = player.upgrade_skill('blink')
    assert success == True
    assert player.skills['blink'] == 1
    assert player.skill_points == 4
    print(f"✓ Upgraded to Blink I: level={player.skills['blink']}, points={player.skill_points}")
    
    # Upgrade to Blink II
    success = player.upgrade_skill('blink')
    assert success == True
    assert player.skills['blink'] == 2
    assert player.skill_points == 3
    print(f"✓ Upgraded to Blink II: level={player.skills['blink']}, points={player.skill_points}")
    
    # Upgrade to Blink III
    success = player.upgrade_skill('blink')
    assert success == True
    assert player.skills['blink'] == 3
    assert player.skill_points == 2
    print(f"✓ Upgraded to Blink III: level={player.skills['blink']}, points={player.skill_points}")
    
    # Upgrade to Blink Master
    success = player.upgrade_skill('blink')
    assert success == True
    assert player.skills['blink'] == 4
    assert player.skill_points == 1
    print(f"✓ Upgraded to Blink Master: level={player.skills['blink']}, points={player.skill_points}")
    
    # Try to upgrade beyond max level
    success = player.upgrade_skill('blink')
    assert success == False
    assert player.skills['blink'] == 4  # Unchanged
    assert player.skill_points == 1  # Unchanged
    print(f"✓ Cannot upgrade beyond Blink Master: level={player.skills['blink']}, points={player.skill_points}")

if __name__ == "__main__":
    try:
        test_blink_config()
        test_can_blink()
        test_activate_blink()
        test_chebyshev_distance()
        test_cooldown_tracking()
        test_upgrade_skill()
        
        print("\n" + "="*50)
        print("✅ ALL BLINK ABILITY TESTS PASSED!")
        print("="*50)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
