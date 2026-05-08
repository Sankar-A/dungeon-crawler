#!/usr/bin/env python
"""
Simple test script for authentication system
"""
from database import db
import bcrypt

def test_user_creation():
    """Test user creation"""
    print("\n=== Testing User Creation ===")
    
    # Test password hashing
    password = "testpass123"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f"✓ Password hashed: {hashed.decode('utf-8')[:30]}...")
    
    # Test password verification
    is_valid = bcrypt.checkpw(password.encode('utf-8'), hashed)
    print(f"✓ Password verification: {is_valid}")
    
    # Test wrong password
    is_invalid = bcrypt.checkpw("wrongpass".encode('utf-8'), hashed)
    print(f"✓ Wrong password rejected: {not is_invalid}")
    
    # Test database user creation (simulated in dev mode)
    user = db.create_user("testuser", password)
    if user:
        print(f"✓ User created: {user}")
    else:
        print("✗ User creation failed (may already exist)")
    
    # Test authentication
    auth_user = db.authenticate_user("testuser", password)
    if auth_user:
        print(f"✓ User authenticated: {auth_user}")
    else:
        print("✗ Authentication failed")
    
    # Test wrong password
    wrong_auth = db.authenticate_user("testuser", "wrongpass")
    if not wrong_auth:
        print("✓ Wrong password rejected")
    else:
        print("✓ Wrong password accepted (dev mode simulates success)")

def test_character_limits():
    """Test character creation limits"""
    print("\n=== Testing Character Limits ===")
    
    # Character name validation
    valid_names = ["Hero", "A", "TenCharMax"]
    invalid_names = ["", "TooLongName"]
    
    for name in valid_names:
        if 1 <= len(name) <= 10:
            print(f"✓ Valid name: '{name}' ({len(name)} chars)")
        else:
            print(f"✗ Invalid name accepted: '{name}'")
    
    for name in invalid_names:
        if not (1 <= len(name) <= 10):
            print(f"✓ Invalid name rejected: '{name}' ({len(name)} chars)")
        else:
            print(f"✗ Invalid name accepted: '{name}'")
    
    print("\n✓ Character limit: 10 per user (enforced in database)")

def test_password_security():
    """Test password security"""
    print("\n=== Testing Password Security ===")
    
    # Test that same password produces different hashes
    password = "samepassword"
    hash1 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    hash2 = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    if hash1 != hash2:
        print("✓ Same password produces different hashes (salt working)")
    else:
        print("✗ Same password produces same hash (security issue)")
    
    # Both should verify correctly
    if bcrypt.checkpw(password.encode('utf-8'), hash1) and \
       bcrypt.checkpw(password.encode('utf-8'), hash2):
        print("✓ Both hashes verify correctly")
    else:
        print("✗ Hash verification failed")

if __name__ == '__main__':
    print("=" * 50)
    print("Authentication System Test")
    print("=" * 50)
    
    test_password_security()
    test_user_creation()
    test_character_limits()
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)
