from flask import request, session, jsonify
from flask_restful import Resource
from server.models import db, User, Recipe

def user_to_dict(user):
    return {
        "id": user.id,
        "username": user.username,
        "image_url": user.image_url,
        "bio": user.bio
    }

class Signup(Resource):
    def post(self):
        data = request.get_json()

        try:
            user = User(
                username=data["username"],
                image_url=data.get("image_url", ""),
                bio=data.get("bio", "")
            )
            user.password_hash = data["password"]  # uses @password_hash.setter
            db.session.add(user)
            db.session.commit()

            session["user_id"] = user.id

            return user_to_dict(user), 201

        except Exception as e:
            return {"errors": [str(e)]}, 422


class Login(Resource):
    def post(self):
        data = request.get_json()
        user = User.query.filter_by(username=data.get("username")).first()

        if user and user.authenticate(data.get("password")):
            session["user_id"] = user.id
            return user_to_dict(user), 200

        return {"error": "Invalid username or password"}, 401


class Logout(Resource):
    def delete(self):
        user_id = session.get("user_id")
        if user_id:
            session.pop("user_id", None)
            return "", 204
        return {"error": "Unauthorized"}, 401


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = db.session.get(User, user_id)  # ✅ SQLAlchemy 2.0+ fix
            if user:
                return user_to_dict(user), 200
        return {"error": "Unauthorized"}, 401


class RecipeIndex(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        recipes = Recipe.query.all()
        return [
            {
                "id": r.id,
                "title": r.title,
                "instructions": r.instructions,
                "minutes_to_complete": r.minutes_to_complete,
                "user": user_to_dict(r.user)
            }
            for r in recipes
        ], 200

    def post(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized"}, 401

        data = request.get_json()

        try:
            recipe = Recipe(
                title=data["title"],
                instructions=data["instructions"],
                minutes_to_complete=data["minutes_to_complete"],
                user_id=user_id
            )
            db.session.add(recipe)
            db.session.commit()

            return {
                "id": recipe.id,
                "title": recipe.title,
                "instructions": recipe.instructions,
                "minutes_to_complete": recipe.minutes_to_complete,
                "user": user_to_dict(recipe.user)
            }, 201

        except Exception as e:
            return {"errors": [str(e)]}, 422
