from models import db, User, Recipe
from faker import Faker
from app import app

fake = Faker()

with app.app_context():
    print("Resetting database...")
    db.drop_all()
    db.create_all()

    # Create one user
    user = User(
        username='Slagathor',
        bio=fake.paragraph(nb_sentences=3),
        image_url=fake.image_url()
    )
    user.password = 'secret'  # ✅ Correct way to set and hash password

    db.session.add(user)
    db.session.commit()

    print("Seeding recipes...")

    # Create 5 recipes with valid data
    for _ in range(5):
        title = fake.sentence(nb_words=4)
        # Ensure instructions are at least 50 characters
        while True:
            instructions = fake.paragraph(nb_sentences=5)
            if len(instructions) >= 50:
                break

        recipe = Recipe(
            title=title,
            instructions=instructions,
            minutes_to_complete=fake.random_int(min=10, max=90),
            user_id=user.id
        )
        db.session.add(recipe)

    db.session.commit()
    print("Database seeded successfully!")
