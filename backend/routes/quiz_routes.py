from flask import Blueprint, request, jsonify
from models.user_model import User
from database.db import get_db_connection
import jwt
import os

quiz_bp = Blueprint('quiz', __name__)
SECRET_KEY = os.getenv("JWT_SECRET", "super_secret_key_change_in_production")

def token_required(f):
    def decorator(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({"error": "Token is missing"}), 401
        try:
            data = jwt.decode(token.split(" ")[1], SECRET_KEY, algorithms=["HS256"])
            current_user_id = data['user_id']
        except Exception:
            return jsonify({"error": "Token is invalid or expired"}), 401
        return f(current_user_id, *args, **kwargs)
    decorator.__name__ = f.__name__
    return decorator

@quiz_bp.route('/submit-quiz', methods=['POST'])
@token_required
def submit_quiz(user_id):
    data = request.get_json()
    responses = data.get('responses')
    if not responses:
        return jsonify({"error": "No responses provided"}), 400

    style_counts = {}
    conn = get_db_connection()
    cur = conn.cursor()

    try:
        for resp in responses:
            style = resp.get('style')
            style_counts[style] = style_counts.get(style, 0) + 1
            cur.execute(
                "INSERT INTO quiz_responses (user_id, question, answer, learning_style_weight) VALUES (?, ?, ?, ?)",
                (user_id, resp['question'], resp['answer'], style)
            )

        conn.commit()
        
        dominant_style = max(style_counts, key=style_counts.get)
        # Close connection so User.update_learning_style can open its own without locking
        conn.close() 
        User.update_learning_style(user_id, dominant_style)
        
        return jsonify({"learning_style": dominant_style}), 200
    except Exception as e:
        print(f"Quiz error: {e}")
        return jsonify({"error": "Failed to submit quiz"}), 500
    finally:
        conn.close()

@quiz_bp.route('/get-learning-style', methods=['GET'])
@token_required
def get_learning_style(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT learning_style FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return jsonify({"learning_style": row['learning_style'] if row else None}), 200
