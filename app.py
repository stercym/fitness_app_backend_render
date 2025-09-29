#!/usr/bin/env python3
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from config import Config
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

db = SQLAlchemy()
migrate = Migrate()
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    CORS(app, supports_credentials=True)
    db.init_app(app)
    jwt = JWTManager()
    jwt.init_app(app)
    migrate.init_app(app, db)

    from models import User, Goal, Workout, Exercise, ExerciseLog
    # Home URL
    @app.route('/')
    def index():
        return jsonify({"message": "Fitness Tracker API is running!"})

    # Users Endpoints
    @app.route("/users", methods=["GET"])
    def get_users():
        users = User.query.all()
        return jsonify([user.to_dict() for user in users]), 200

    @app.route("/users", methods=["POST"])
    def create_user():
        data = request.get_json()

        if not data:
            return jsonify({"error": "No input data provided"}), 400

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        goal_name = data.get("goal") 

        if not name or not email or not password:
            return jsonify({"error": "Missing required fields"}), 400

        # Create user
        new_user = User(name=name, email=email)
        new_user.set_password(password)

        # Attach goal if provided
        if goal_name:
            goal = Goal.query.filter_by(name=goal_name).first()
            if goal:
                new_user.goals.append(goal)

        db.session.add(new_user)
        db.session.commit()

        return jsonify({
            "message": "User created successfully",
            "user": new_user.to_dict()
        }), 201

    
    @app.route("/users/<int:id>", methods=["PATCH"])
    def update_user(id):
        user = User.query.get_or_404(id)
        data = request.get_json()
        user.name = data.get("name", user.name)
        user.email = data.get("email", user.email)
        db.session.commit()
        return jsonify(user.to_dict()), 200

    @app.route("/users/<int:id>", methods=["DELETE"])
    def delete_user(id):
        user = User.query.get_or_404(id)
        db.session.delete(user)
        db.session.commit()
        return jsonify({"message": "User deleted"}), 204

    # Goals Endpoints
    @app.route("/goals", methods=["GET"])
    def get_goals():
        goals = Goal.query.all()
        return jsonify([goal.to_dict() for goal in goals]), 200

    @app.route("/goals", methods=["POST"])
    def create_goal():
        data = request.get_json()
        new_goal = Goal(name=data["name"])
        db.session.add(new_goal)
        db.session.commit()
        return jsonify(new_goal.to_dict()), 201
    
    @app.route("/goals/<int:id>", methods=["PATCH"])
    def update_goal(id):
        goal = Goal.query.get_or_404(id)
        data = request.get_json()
        goal.name = data.get("name", goal.name)
        db.session.commit()
        return jsonify(goal.to_dict()), 200

    @app.route("/goals/<int:id>", methods=["DELETE"])
    def delete_goal(id):
        goal = Goal.query.get_or_404(id)
        db.session.delete(goal)
        db.session.commit()
        return jsonify({"message": "Goal deleted"}), 204
    
    # Exercises Endpoints
    @app.route("/exercises", methods=["GET"])
    def get_exercises():
        exercises = Exercise.query.all()
        return jsonify([
            {"id": e.id, "name": e.exercise_name, "goal_id": e.goal_id} for e in exercises
        ])

    @app.route("/exercises", methods=["POST"])
    def create_exercise():
        data = request.get_json()
        new_exercise = Exercise(exercise_name=data["exercise_name"], goal_id=data["goal_id"])
        db.session.add(new_exercise)
        db.session.commit()
        return jsonify(new_exercise.to_dict()), 201
    
    @app.route("/exercises/<int:id>", methods=["PATCH"])
    def update_exercise(id):
        exercise = Exercise.query.get_or_404(id)
        data = request.get_json()
        exercise.name = data.get("name", exercise.exercise_name)
        exercise.goal_id = data.get("goal_id", exercise.goal_id)
        db.session.commit()
        return jsonify(exercise.to_dict()), 200

    @app.route("/exercises/<int:id>", methods=["DELETE"])
    def delete_exercise(id):
        exercise = Exercise.query.get_or_404(id)
        db.session.delete(exercise)
        db.session.commit()
        return jsonify({"message": "Exercise deleted"}), 204
    
    # Workouts Endpoints
    @app.route("/workouts", methods=["GET"])
    def get_workouts():
        workouts = Workout.query.all()
        return jsonify([
            {"id": w.id, "title": w.title, "date": w.date, "user_id": w.user_id} for w in workouts
        ])

    @app.route("/workouts", methods=["POST"])
    def create_workout():
        data = request.get_json()
        new_workout = Workout(title=data["title"], date=data["date"], user_id=data["user_id"])
        db.session.add(new_workout)
        db.session.commit()
        return jsonify(new_workout.to_dict()), 201
    
    @app.route("/workouts/<int:id>", methods=["PATCH"])
    def update_workout(id):
        workout = Workout.query.get_or_404(id)
        data = request.get_json()
        workout.title = data.get("title", workout.title)
        workout.date = data.get("date", workout.date)
        workout.user_id = data.get("user_id", workout.user_id)
        db.session.commit()
        return jsonify(workout.to_dict()), 200

    @app.route("/workouts/<int:id>", methods=["DELETE"])
    def delete_workout(id):
        workout = Workout.query.get_or_404(id)
        db.session.delete(workout)
        db.session.commit()
        return jsonify({"message": "Workout deleted"}), 204
    
    # Exercise Logs Endpoints
    @app.route("/exercise_logs", methods=["GET"])
    def get_logs():
        logs = ExerciseLog.query.all()
        return jsonify([
            {
                "id": log.id,
                "sets": log.sets,
                "reps": log.reps,
                "weight": log.weight,
                "workout_id": log.workout_id,
                "exercise_id": log.exercise_id
            } for log in logs
        ])

    @app.route("/exercise_logs", methods=["POST"])
    def create_log():
        data = request.get_json()
        new_log = ExerciseLog(
            sets=data["sets"],
            reps=data["reps"],
            weight=data.get("weight", 0),
            workout_id=data["workout_id"],
            exercise_id=data["exercise_id"]
        )
        db.session.add(new_log)
        db.session.commit()
        return jsonify(new_log.to_dict()), 201
    
    @app.route("/exercise_logs/<int:id>", methods=["PATCH"])
    def update_log(id):
        log = ExerciseLog.query.get_or_404(id)
        data = request.get_json()
        log.sets = data.get("sets", log.sets)
        log.reps = data.get("reps", log.reps)
        log.weight = data.get("weight", log.weight)
        log.workout_id = data.get("workout_id", log.workout_id)
        log.exercise_id = data.get("exercise_id", log.exercise_id)
        db.session.commit()
        return jsonify(log.to_dict()), 200

    @app.route("/exercise_logs/<int:id>", methods=["DELETE"])
    def delete_log(id):
        log = ExerciseLog.query.get_or_404(id)
        db.session.delete(log)
        db.session.commit()
        return jsonify({"message": "Exercise log deleted"}), 204

        # Authentication Endpoints
    @app.route("/auth/register", methods=["POST"])
    def auth_register():
        """
        Expects JSON: { name, email, password, goal_id (optional) }
        Creates user with hashed password. Returns created user (no password).
        """
        data = request.get_json() or {}
        name = data.get("name")
        email = data.get("email")
        password = data.get("password")
        goal_id = data.get("goal_id")

        if not name or not email or not password:
            return jsonify({"error": "name, email and password are required"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"error": "email already registered"}), 409

        user = User(name=name, email=email)
        user.set_password(password)

        if goal_id:
            goal = Goal.query.get(goal_id)
            if goal:
                user.goals.append(goal)


    # Login authentication
    @app.route("/auth/login", methods=["POST"])
    def auth_login():
        """
        Expects JSON: { email, password }
        Returns: { access_token, user }
        """
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"error": "email and password are required"}), 400

        user = User.query.filter_by(email=email).first()
        if not user or not user.check_password(password):
            return jsonify({"error": "invalid credentials"}), 401

        access_token = create_access_token(identity=user.id)
        return jsonify({"access_token": access_token, "user": user.to_dict()}), 200


    # shows current user info
    @app.route("/users/me", methods=["GET"])
    @jwt_required()
    def users_me():
        current_user_id = get_jwt_identity()
        user = User.query.get_or_404(current_user_id)
        return jsonify(user.to_dict()), 200
    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
