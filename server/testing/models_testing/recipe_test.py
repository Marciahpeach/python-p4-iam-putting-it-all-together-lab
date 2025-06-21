import pytest
from sqlalchemy.exc import IntegrityError
from server.app import app
from server.models import db, User, Recipe


class TestRecipe:
    '''Recipe in models.py'''

    def setup_method(self):
        with app.app_context():
            db.drop_all()
            db.create_all()

            self.user = User(
                username="testuser",
                image_url="https://example.com/image.jpg",
                bio="Sample bio"
            )
            self.user.password = "securepassword"
            db.session.add(self.user)
            db.session.commit()

    def test_has_attributes(self):
        '''has attributes title, instructions, and minutes_to_complete.'''
        with app.app_context():
            recipe = Recipe(
                title="Delicious Shed Ham",
                instructions=(
                    "Or kind rest bred with am shed then. In raptures building "
                    "an bringing be. Elderly is detract tedious assured private "
                    "so to visited. Do travelling companions contrasted it. "
                    "Mistress strongly remember up to. Ham him compass you proceed "
                    "calling detract. Better of always missed we person mr. September "
                    "smallness northward situation few her certainty something."
                ),
                minutes_to_complete=60,
                user_id=self.user.id
            )
            db.session.add(recipe)
            db.session.commit()

            new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()
            assert new_recipe.title == "Delicious Shed Ham"
            assert new_recipe.instructions.startswith("Or kind rest bred with am shed then")
            assert new_recipe.minutes_to_complete == 60

    def test_requires_title(self):
        '''requires each record to have a title.'''
        with app.app_context():
            recipe = Recipe(
                instructions="A long enough instruction to pass validation.",
                minutes_to_complete=30,
                user_id=self.user.id
            )
            with pytest.raises(IntegrityError):
                db.session.add(recipe)
                db.session.commit()

    def test_requires_50_plus_char_instructions(self):
        '''requires instructions to be at least 50 characters long.'''
        with app.app_context():
            short_instruction = "Too short."
            with pytest.raises(ValueError):
                recipe = Recipe(
                    title="Short Instructions Recipe",
                    instructions=short_instruction,
                    minutes_to_complete=20,
                    user_id=self.user.id
                )
                db.session.add(recipe)
                db.session.commit()
