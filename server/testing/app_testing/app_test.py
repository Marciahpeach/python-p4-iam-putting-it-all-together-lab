from faker import Faker
from random import randint
import pytest

from server.app import app
from models import db, User, Recipe

app.secret_key = b'a\xdb\xd2\x13\x93\xc1\xe9\x97\xef2\xe3\x004U\xd1Z'
fake = Faker()

class TestSignup:
    def test_creates_users_at_signup(self):
        '''creates user records with usernames and passwords at /signup.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            response = client.post('/signup', json={
                'username': 'ashketchum',
                'password': 'pikachu',
                'bio': fake.paragraph(),
                'image_url': fake.url(),
            })
            assert response.status_code == 201

            new_user = User.query.filter(User.username == 'ashketchum').first()
            assert new_user
            assert new_user.authenticate('pikachu')

    def test_422s_invalid_users_at_signup(self):
        '''422s invalid usernames at /signup.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            response = client.post('/signup', json={
                'password': 'pikachu',
                'bio': fake.paragraph(),
                'image_url': fake.url(),
            })
            assert response.status_code == 422


class TestCheckSession:
    def test_returns_user_json_for_active_session(self):
        '''returns JSON for the user's data if there is an active session.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            client.post('/signup', json={
                'username': 'ashketchum',
                'password': 'pikachu',
                'bio': fake.paragraph(),
                'image_url': fake.url(),
            })

            with client.session_transaction() as session:
                session['user_id'] = 1

            response = client.get('/check_session')
            assert response.status_code == 200
            assert response.get_json()['id'] == 1

    def test_401s_for_no_session(self):
        '''returns 401 Unauthorized status code if no active session.'''
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = None

            response = client.get('/check_session')
            assert response.status_code == 401


class TestLogin:
    def test_logs_in(self):
        '''logs users in with username and password at /login.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            client.post('/signup', json={
                'username': 'ashketchum',
                'password': 'pikachu',
                'bio': fake.paragraph(),
                'image_url': fake.url(),
            })

            response = client.post('/login', json={
                'username': 'ashketchum',
                'password': 'pikachu',
            })
            assert response.status_code == 200
            assert response.get_json()['username'] == 'ashketchum'

            with client.session_transaction() as session:
                assert session.get('user_id') == User.query.filter_by(username='ashketchum').first().id

    def test_401s_bad_logins(self):
        with app.app_context():
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            response = client.post('/login', json={
                'username': 'fakeuser',
                'password': 'wrongpass',
            })
            assert response.status_code == 401


class TestLogout:
    def test_logs_out(self):
        '''logs users out at /logout.'''
        with app.app_context():
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            client.post('/signup', json={'username': 'ashketchum', 'password': 'pikachu'})
            client.post('/login', json={'username': 'ashketchum', 'password': 'pikachu'})
            client.delete('/logout')

            with client.session_transaction() as session:
                assert not session.get('user_id')

    def test_401s_if_no_session(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = None
            response = client.delete('/logout')
            assert response.status_code == 401


class TestRecipeIndex:
    def test_lists_recipes_with_200(self):
        '''returns user's recipes with a 200 status.'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(
                username="Slagathor",
                bio=fake.paragraph(),
                image_url=fake.url()
            )
            user.password = 'secret'
            db.session.add(user)
            db.session.commit()

            recipes = [
                Recipe(
                    title=fake.sentence(),
                    instructions=fake.paragraph(nb_sentences=8),
                    minutes_to_complete=randint(15, 90),
                    user=user
                ) for _ in range(15)
            ]
            db.session.add_all(recipes)
            db.session.commit()

        with app.test_client() as client:
            client.post('/login', json={'username': 'Slagathor', 'password': 'secret'})
            response = client.get('/recipes')
            assert response.status_code == 200
            data = response.get_json()
            assert len(data) == 15

    def test_get_route_returns_401_when_not_logged_in(self):
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

        with app.test_client() as client:
            with client.session_transaction() as session:
                session['user_id'] = None
            response = client.get('/recipes')
            assert response.status_code == 401

    def test_creates_recipes_with_201(self):
        '''creates recipes associated with the logged-in user'''
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(
                username="Slagathor",
                bio=fake.paragraph(),
                image_url=fake.url()
            )
            user.password = 'secret'
            db.session.add(user)
            db.session.commit()

        with app.test_client() as client:
            client.post('/login', json={'username': 'Slagathor', 'password': 'secret'})
            response = client.post('/recipes', json={
                'title': fake.sentence(),
                'instructions': fake.paragraph(nb_sentences=8),
                'minutes_to_complete': randint(15, 90)
            })
            assert response.status_code == 201
            data = response.get_json()
            assert data['title']
            assert data['instructions']
            assert data['minutes_to_complete']

    def test_returns_422_for_invalid_recipes(self):
        with app.app_context():
            Recipe.query.delete()
            User.query.delete()
            db.session.commit()

            user = User(
                username="Slagathor",
                bio=fake.paragraph(),
                image_url=fake.url()
            )
            user.password = 'secret'
            db.session.add(user)
            db.session.commit()

        with app.test_client() as client:
            client.post('/login', json={'username': 'Slagathor', 'password': 'secret'})
            response = client.post('/recipes', json={
                'title': fake.sentence(),
                'instructions': 'too short',
                'minutes_to_complete': randint(15, 90)
            })
            assert response.status_code == 422
