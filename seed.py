#!/usr/bin/env python3
from app import create_app, db
from models import Goal

# Predefined goals to match frontend dropdown
GOALS = [
    "lose_weight",
    "gain_muscle",
    "add_weight",
    "stay_fit",
    "grow_glutes",
]

app = create_app()

with app.app_context():
    for goal_name in GOALS:
        # Only add if it doesn't exist
        existing = Goal.query.filter_by(name=goal_name).first()
        if not existing:
            new_goal = Goal(name=goal_name)
            db.session.add(new_goal)
            print(f"Added goal: {goal_name}")
        else:
            print(f"Goal already exists: {goal_name}")
    
    db.session.commit()
    print("Seeding complete")
