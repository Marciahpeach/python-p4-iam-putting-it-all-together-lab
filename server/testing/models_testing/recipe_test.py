import pytest
from sqlalchemy.exc import IntegrityError
from server.app import app
from server.models import db, User, Recipe

@pytest.fixture(autouse=True)
def run_around_tests():
    # Set up and tear down the database for each test
    with app.app_context():
        db.drop_all()
        db.create_all()

        user = User(
            username="testuser",
            image_url="https://example.com/image.jpg",
            bio="Sample bio"
        )
        user.password = "securepassword"
        db.session.add(user)
        db.session.commit()

        yield {'user': user}

        db.session.remove()
        db.drop_all()


def test_has_attributes(run_around_tests):
    '''has attributes title, instructions, and minutes_to_complete.'''
    user = run_around_tests['user']
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
        user_id=user.id
    )
    db.session.add(recipe)
    db.session.commit()

    new_recipe = Recipe.query.filter_by(title="Delicious Shed Ham").first()
    assert new_recipe.title == "Delicious Shed Ham"
    assert new_recipe.instructions.startswith("Or kind rest bred with am shed then")
    assert new_recipe.minutes_to_complete == 60


def test_requires_title(run_around_tests):
    '''requires each record to have a title.'''
    user = run_around_tests['user']
    with pytest.raises(ValueError):
        recipe = Recipe(
            title=None,
            instructions="A long enough instruction to pass validation. " * 2,
            minutes_to_complete=30,
            user_id=user.id
        )
        db.session.add(recipe)
        db.session.commit()


def test_requires_50_plus_char_instructions(run_around_tests):
    '''requires instructions to be at least 50 characters long.'''
    user = run_around_tests['user']
    short_instruction = "Too short."
    with pytest.raises(ValueError):
        recipe = Recipe(
            title="Short Instructions Recipe",
            instructions=short_instruction,
            minutes_to_complete=20,
            user_id=user.id
        )
        db.session.add(recipe)
        db.session.commit()
