from server.app import app, db
from server.models import User, Recipe

with app.app_context():
    print("🧹 Clearing old data...")
    Recipe.query.delete()
    User.query.delete()

    print("🌱 Seeding users and recipes...")

    user1 = User(
        username="ashketchum",
        image_url="https://example.com/ash.png",
        bio="I want to be the very best!"
    )
    user1.password_hash = "pikachu"

    user2 = User(
        username="mistywater",
        image_url="https://example.com/misty.png",
        bio="Leader of Cerulean Gym"
    )
    user2.password_hash = "togepi"

    db.session.add_all([user1, user2])
    db.session.commit()

    recipe1 = Recipe(
        title="Poke Puffs",
        instructions="First gather berries, then mix them carefully into flour and bake them at 180 degrees for 20 minutes until golden brown.",
        minutes_to_complete=30,
        user_id=user1.id
    )

    recipe2 = Recipe(
        title="Seafood Surprise",
        instructions="Begin with fresh caught Magikarp. Gut it, season with salt and pepper, and simmer with vegetables for 45 minutes until tender.",
        minutes_to_complete=45,
        user_id=user2.id
    )

    db.session.add_all([recipe1, recipe2])
    db.session.commit()
    print("✅ Seeded!")
