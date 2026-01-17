#!/usr/bin/env python3
"""
Test script for the authentication and profile system
"""
from app import app, db, User, Goal
from datetime import datetime, timezone

def test_authentication_system():
    print("🧪 Testing Authentication System\n")
    
    with app.app_context():
        # Create fresh tables
        db.drop_all()
        db.create_all()
        print("✓ Database tables recreated")

        # Test 1: Create a regular user
        print("\n1. Testing user registration...")
        user1 = User(username="testuser", email="test@example.com")
        user1.set_password("password123")
        db.session.add(user1)
        db.session.commit()
        print("✓ Regular user created")

        # Test 2: Password verification
        print("\n2. Testing password verification...")
        assert user1.check_password("password123"), "Password should match"
        assert not user1.check_password("wrongpassword"), "Wrong password should not match"
        print("✓ Password hashing and verification working")

        # Test 3: Create guest user
        print("\n3. Testing guest user creation...")
        guest_user = User.create_guest()
        db.session.add(guest_user)
        db.session.commit()
        print(f"✓ Guest user created: {guest_user.username} (token: {guest_user.guest_token[:8]}...)")

        # Test 4: Multi-tenant goal isolation
        print("\n4. Testing goal isolation...")
        
        # Create goals for regular user
        user1_goal = Goal(text="User 1's goal", goal_type="daily", user_id=user1.id)
        db.session.add(user1_goal)
        
        # Create goals for guest user
        guest_goal = Goal(text="Guest's goal", goal_type="daily", user_id=guest_user.id)
        db.session.add(guest_goal)
        
        db.session.commit()
        
        # Verify isolation
        user1_goals = Goal.query.filter_by(user_id=user1.id).all()
        guest_goals = Goal.query.filter_by(user_id=guest_user.id).all()
        
        assert len(user1_goals) == 1 and user1_goals[0].text == "User 1's goal"
        assert len(guest_goals) == 1 and guest_goals[0].text == "Guest's goal"
        print("✓ Goal isolation working correctly")

        # Test 5: Guest conversion simulation
        print("\n5. Testing guest to registered user conversion...")
        
        # Convert guest to regular user
        guest_user.username = "converted_user"
        guest_user.email = "converted@example.com"
        guest_user.set_password("newpassword123")
        guest_user.is_guest = False
        guest_user.guest_token = None
        
        db.session.commit()
        
        # Verify conversion
        converted_user = User.query.filter_by(username="converted_user").first()
        assert converted_user is not None
        assert not converted_user.is_guest
        assert converted_user.check_password("newpassword123")
        
        # Verify goals are still there
        converted_goals = Goal.query.filter_by(user_id=converted_user.id).all()
        assert len(converted_goals) == 1 and converted_goals[0].text == "Guest's goal"
        print("✓ Guest conversion working correctly")

        # Test 6: User profile data
        print("\n6. Testing user profile features...")
        
        user1.display_name = "Test User Display"
        user1.timezone = "America/New_York"
        db.session.commit()
        
        profile_data = user1.to_dict()
        assert profile_data['display_name'] == "Test User Display"
        assert profile_data['timezone'] == "America/New_York"
        assert 'password_hash' not in profile_data  # Should not expose sensitive data
        print("✓ User profile management working")

        # Test 7: Database relationships
        print("\n7. Testing database relationships...")
        
        # Test user -> goals relationship
        assert len(user1.goals) == 1
        assert user1.goals[0].text == "User 1's goal"
        
        # Test goal -> user relationship
        goal = Goal.query.first()
        assert goal.user.username in ["testuser", "converted_user"]
        print("✓ Database relationships working")

        # Test 8: Data serialization
        print("\n8. Testing data serialization...")
        
        user_dict = user1.to_dict()
        goal_dict = user1_goal.to_dict()
        
        assert isinstance(user_dict['created_at'], str)  # Should be ISO format
        assert isinstance(goal_dict['created'], str)     # Should be ISO format
        print("✓ Data serialization working")

        print("\n🎉 All authentication tests passed!")
        
        # Summary
        print("\n📊 Test Summary:")
        print(f"  - Total users: {User.query.count()}")
        print(f"  - Regular users: {User.query.filter_by(is_guest=False).count()}")
        print(f"  - Guest users: {User.query.filter_by(is_guest=True).count()}")
        print(f"  - Total goals: {Goal.query.count()}")
        
        return True

if __name__ == "__main__":
    test_authentication_system()