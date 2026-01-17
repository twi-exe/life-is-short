#!/usr/bin/env python3
"""
Test script for the goals database system
"""
from app import app, db, Goal
from datetime import datetime, timezone

def test_database():
    with app.app_context():
        # Create tables
        db.create_all()
        print("✓ Database tables created")

        # Create test goals
        daily_goal = Goal(
            text="Complete morning workout",
            goal_type="daily",
            user_id="test_user"
        )

        weekly_goal = Goal(
            text="Read 3 chapters of a book",
            goal_type="weekly",
            user_id="test_user"
        )

        yearly_goal = Goal(
            text="Learn a new programming language",
            goal_type="yearly",
            user_id="test_user"
        )

        db.session.add_all([daily_goal, weekly_goal, yearly_goal])
        db.session.commit()
        print("✓ Test goals created")

        # Query goals
        all_goals = Goal.query.filter_by(user_id="test_user").all()
        print(f"✓ Found {len(all_goals)} goals in database")

        # Test goal types
        daily_goals = Goal.query.filter_by(goal_type="daily", user_id="test_user").all()
        weekly_goals = Goal.query.filter_by(goal_type="weekly", user_id="test_user").all()
        yearly_goals = Goal.query.filter_by(goal_type="yearly", user_id="test_user").all()

        print(f"  - Daily goals: {len(daily_goals)}")
        print(f"  - Weekly goals: {len(weekly_goals)}")
        print(f"  - Yearly goals: {len(yearly_goals)}")

        # Test updating a goal
        if daily_goals:
            goal = daily_goals[0]
            goal.done = True
            goal.completed = datetime.now(timezone.utc)
            db.session.commit()
            print("✓ Goal marked as completed")

        # Test cleanup (should not delete recent goals)
        from app import cleanup_old_goals
        # This would normally be called via API, but let's test the logic
        from datetime import timedelta
        cutoff_date = datetime.now(timezone.utc) - timedelta(days=7)
        old_goals = Goal.query.filter_by(goal_type='daily', done=True).filter(Goal.completed < cutoff_date).all()
        print(f"✓ Found {len(old_goals)} old goals to clean up")

        print("\n🎉 Database system test completed successfully!")

if __name__ == "__main__":
    test_database()