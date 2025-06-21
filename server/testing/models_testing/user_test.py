import pytest
from sqlalchemy.exc import IntegrityError
from server.app import app, db  # ✅ FIX: use the db instance from app
from server.models import User, Recipe


class TestUser:
    '''User in models.py'''

    def test_has_attributes(self):
        '''has attributes username, _password_hash, image_url, and bio.'''

        with app.app_context():
            db.drop_all()
            db.create_all()

            user = User(
                username="Liz",
                image_url="https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg",
                bio="Dame Elizabeth Rosemond Taylor DBE (February 27, 1932 - March 23, 2011) was a British-American actress."
            )
            user.password = "whosafraidofvirginiawoolf"  # ✅ use the write-only property

            db.session.add(user)
            db.session.commit()

            created_user = User.query.filter_by(username="Liz").first()

            assert created_user.username == "Liz"
            assert created_user.image_url == "https://prod-images.tcm.com/Master-Profile-Images/ElizabethTaylor.jpg"
            assert "Elizabeth Rosemond Taylor" in created_user.bio

            with pytest.raises(AttributeError):
                _ = created_user.password_hash  # ✅ properly trigger the AttributeError

    def test_requires_username(self):
        '''requires each record to have a username.'''
        with app.app_context():
            db.drop_all()
            db.create_all()

            user = User()
            with pytest.raises(IntegrityError):
                db.session.add(user)
                db.session.commit()

    def test_requires_unique_username(self):
        '''requires username to be unique.'''
        with app.app_context():
            db.drop_all()
            db.create_all()

            user_1 = User(username="Ben")
            user_2 = User(username="Ben")

            with pytest.raises(IntegrityError):
                db.session.add_all([user_1, user_2])
                db.session.commit()

    def test_has_list_of_recipes(self):
        '''has records with lists of recipes records attached.'''
        with app.app_context():
            db.drop_all()
            db.create_all()

            user = User(username="Prabhdip")

            recipe_1 = Recipe(
                title="Delicious Shed Ham",
                instructions="Or kind rest bred with am shed then. In raptures building an bringing be. Elderly is detract...",
                minutes_to_complete=60,
            )
            recipe_2 = Recipe(
                title="Hasty Party Ham",
                instructions="As am hastily invited settled at limited civilly fortune me. Really spring in extent an by...",
                minutes_to_complete=30,
            )

            user.recipes.extend([recipe_1, recipe_2])
            db.session.add(user)
            db.session.commit()

            assert user.id
            assert recipe_1.id
            assert recipe_2.id
            assert recipe_1 in user.recipes
            assert recipe_2 in user.recipes
