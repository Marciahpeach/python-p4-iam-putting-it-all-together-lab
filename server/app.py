# server/app.py

from flask import Flask, request, session, jsonify
from flask_migrate import Migrate
from flask_cors import CORS
from models import db, User, Recipe, bcrypt
from config import Config

# Initialize app and config
app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for cross-origin requests with cookies
CORS(app, supports_credentials=True)

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)
migrate = Migrate(app, db)

# ------------------- Routes -------------------

@app.post('/signup')
def signup():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        bio = data.get('bio')
        image_url = data.get('image_url')

        if not username or not password:
            raise ValueError("Username and password are required.")

        user = User(username=username, bio=bio, image_url=image_url)
        user.password = password  # Hashing happens in the setter

        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

        return jsonify({
            "id": user.id,
            "username": user.username,
            "bio": user.bio,
            "image_url": user.image_url
        }), 201

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 422


@app.get('/check_session')
def check_session():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 401

    return jsonify({
        "id": user.id,
        "username": user.username,
        "bio": user.bio,
        "image_url": user.image_url
    }), 200


@app.post('/login')
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            raise ValueError("Username and password are required.")

        user = User.query.filter_by(username=username).first()

        if user and user.authenticate(password):
            session['user_id'] = user.id
            return jsonify({
                "id": user.id,
                "username": user.username,
                "bio": user.bio,
                "image_url": user.image_url
            }), 200

        return jsonify({"error": "Unauthorized"}), 401

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 422


@app.delete('/logout')
def logout():
    if not session.get('user_id'):
        return jsonify({"error": "Unauthorized"}), 401

    session.clear()
    return '', 204


@app.get('/recipes')
def get_recipes():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    recipes = Recipe.query.all()
    return jsonify([
        {
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {
                "id": recipe.user.id,
                "username": recipe.user.username,
                "bio": recipe.user.bio,
                "image_url": recipe.user.image_url
            }
        }
        for recipe in recipes
    ]), 200


@app.post('/recipes')
def create_recipe():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()

        recipe = Recipe(
            title=data.get('title'),
            instructions=data.get('instructions'),
            minutes_to_complete=data.get('minutes_to_complete'),
            user_id=user_id
        )

        db.session.add(recipe)
        db.session.commit()

        return jsonify({
            "id": recipe.id,
            "title": recipe.title,
            "instructions": recipe.instructions,
            "minutes_to_complete": recipe.minutes_to_complete,
            "user": {
                "id": recipe.user.id,
                "username": recipe.user.username,
                "bio": recipe.user.bio,
                "image_url": recipe.user.image_url
            }
        }), 201

    except Exception as e:
        return jsonify({"errors": [str(e)]}), 422

# ------------------- Run Server -------------------

if __name__ == '__main__':
    app.run(port=5555, debug=True)
