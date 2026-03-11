from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database.db import init_db
from routes.auth_routes import auth_bp
from routes.quiz_routes import quiz_bp
from routes.recommendation_routes import recommendation_bp

load_dotenv()

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# Initialize database
init_db()

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
app.register_blueprint(recommendation_bp, url_prefix='/api/recommendation')

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    port = int(os.getenv("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
