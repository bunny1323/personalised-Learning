from flask import Blueprint, request, jsonify
from models.user_model import User
from database.db import get_db_connection
import jwt
import datetime
import os
import bcrypt

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_key_change_in_production")

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password') or not data.get('name'):
        return jsonify({"error": "Missing required fields"}), 400

    if User.find_by_email(data['email']):
        return jsonify({"error": "User already exists"}), 400

    user = User.create(data['name'], data['email'], data['password'])
    if user:
        return jsonify({"message": "Registered successfully!", "user": user}), 201
    return jsonify({"error": "Registration failed"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({"error": "Missing credentials"}), 400

    user = User.find_by_email(data['email'])
    if user and bcrypt.checkpw(data['password'].encode('utf-8'), user['password_hash'].encode('utf-8')):
        streak = User.update_streak(user['id'])
        token = jwt.encode({
            'user_id': user['id'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm="HS256")

        return jsonify({
            "token": token,
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "learning_style": user['learning_style'],
                "streak_count": streak
            }
        }), 200

    return jsonify({"error": "Invalid email or password"}), 401
