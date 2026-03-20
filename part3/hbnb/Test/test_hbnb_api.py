"""
HBnB API — Suite de tests complète
Couvre : Auth, Users, Amenities, Places, Reviews
         Validations, Contrôle d'accès JWT, Cas limites, Intégration

Lancement (depuis part3/hbnb/ avec le venv activé) :
    source ../.venv/bin/activate
    python3 -m pytest Test/test_hbnb_api.py -v
    python3 -m unittest discover -s Test -p "test_*.py" -v
"""

import unittest
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'  ))

from app import create_app, db


class BaseTestCase(unittest.TestCase):
    """Classe de base — chaque test repart d'une DB SQLite in-memory vide."""

    def setUp(self):
        self.app = create_app("config.TestingConfig")
        self.client = self.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    # ------------------------------------------------------------------ #
    # HTTP helpers
    # ------------------------------------------------------------------ #

    def post_json(self, url, data, headers=None):
        return self.client.post(url, data=json.dumps(data),
                                content_type='application/json',
                                headers=headers or {})

    def put_json(self, url, data, headers=None):
        return self.client.put(url, data=json.dumps(data),
                               content_type='application/json',
                               headers=headers or {})

    def delete(self, url, headers=None):
        return self.client.delete(url, headers=headers or {})

    def get(self, url, headers=None):
        return self.client.get(url, headers=headers or {})

    # ------------------------------------------------------------------ #
    # Auth helpers
    # ------------------------------------------------------------------ #

    def get_token(self, email, password):
        resp = self.post_json('/api/v1/auth/login',
                              {"email": email, "password": password})
        return resp.get_json().get('access_token')

    def auth_header(self, token):
        return {"Authorization": f"Bearer {token}"}

    # ------------------------------------------------------------------ #
    # DB helpers — insertion directe sans passer par l'API
    # ------------------------------------------------------------------ #

    def _insert_user(self, email="user@test.com", password="userpass",
                     first_name="John", last_name="Doe", is_admin=False):
        from app.models.user import User
        with self.app.app_context():
            user = User(first_name=first_name, last_name=last_name,
                        email=email, password=password, is_admin=is_admin)
            db.session.add(user)
            db.session.commit()
            user_id = user.id
        token = self.get_token(email, password)
        return user_id, token

    def create_admin_and_token(self, email="admin@test.com", password="adminpass"):
        return self._insert_user(email=email, password=password,
                                  first_name="Admin", last_name="Root",
                                  is_admin=True)

    def create_regular_user_and_token(self, email="user@test.com",
                                       password="userpass",
                                       first_name="John", last_name="Doe"):
        return self._insert_user(email=email, password=password,
                                  first_name=first_name, last_name=last_name,
                                  is_admin=False)

    # ------------------------------------------------------------------ #
    # API helpers
    # ------------------------------------------------------------------ #

    def create_user_via_api(self, admin_token, email="john@example.com",
                             password="pass123", first_name="John",
                             last_name="Doe"):
        return self.post_json('/api/v1/users/',
                              {"first_name": first_name, "last_name": last_name,
                               "email": email, "password": password},
                              headers=self.auth_header(admin_token))

    def create_amenity(self, admin_token, name="WiFi"):
        return self.post_json('/api/v1/amenities/', {"name": name},
                               headers=self.auth_header(admin_token))

    def create_place(self, owner_token, owner_id, title="Nice Place",
                     description="A great spot", price=99.9,
                     latitude=48.8566, longitude=2.3522, amenity_ids=None):
        return self.post_json('/api/v1/places/',
                              {"title": title, "description": description,
                               "price": price, "latitude": latitude,
                               "longitude": longitude, "owner_id": owner_id,
                               "amenities": amenity_ids or []},
                              headers=self.auth_header(owner_token))

    def create_review(self, reviewer_token, reviewer_id, place_id,
                       text="Great!", rating=5):
        return self.post_json('/api/v1/reviews/',
                              {"text": text, "rating": rating,
                               "user_id": reviewer_id, "place_id": place_id},
                              headers=self.auth_header(reviewer_token))

    # ------------------------------------------------------------------ #
    # Scenario helpers
    # ------------------------------------------------------------------ #

    def setup_owner_and_place(self, owner_email="owner@t.com"):
        owner_id, owner_token = self.create_regular_user_and_token(
            email=owner_email)
        place_id = self.create_place(owner_token, owner_id).get_json()['id']
        return owner_id, owner_token, place_id

    def setup_review_scenario(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="reviewer@t.com")
        review_id = self.create_review(
            reviewer_token, reviewer_id, place_id).get_json()['id']
        return (owner_id, owner_token, reviewer_id,
                reviewer_token, place_id, review_id)


# ======================================================================
# AUTH
# ======================================================================

class TestAuth(BaseTestCase):

    def test_login_admin_returns_token(self):
        self.create_admin_and_token()
        resp = self.post_json('/api/v1/auth/login',
                              {"email": "admin@test.com", "password": "adminpass"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access_token', resp.get_json())

    def test_login_token_is_string(self):
        self.create_admin_and_token()
        token = self.get_token("admin@test.com", "adminpass")
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 10)

    def test_login_regular_user_returns_token(self):
        self.create_regular_user_and_token()
        resp = self.post_json('/api/v1/auth/login',
                              {"email": "user@test.com", "password": "userpass"})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('access_token', resp.get_json())

    def test_login_wrong_password_returns_401(self):
        self.create_admin_and_token()
        resp = self.post_json('/api/v1/auth/login',
                              {"email": "admin@test.com", "password": "wrong"})
        self.assertEqual(resp.status_code, 401)

    def test_login_unknown_email_returns_401(self):
        resp = self.post_json('/api/v1/auth/login',
                              {"email": "ghost@test.com", "password": "pass"})
        self.assertEqual(resp.status_code, 401)

    def test_login_missing_password_field(self):
        resp = self.post_json('/api/v1/auth/login',
                              {"email": "admin@test.com"})
        self.assertIn(resp.status_code, [400, 401])

    def test_login_missing_email_field(self):
        resp = self.post_json('/api/v1/auth/login', {"password": "pass"})
        self.assertIn(resp.status_code, [400, 401])

    def test_login_empty_payload(self):
        resp = self.post_json('/api/v1/auth/login', {})
        self.assertIn(resp.status_code, [400, 401])

    def test_login_response_has_no_password(self):
        self.create_admin_and_token()
        resp = self.post_json('/api/v1/auth/login',
                              {"email": "admin@test.com", "password": "adminpass"})
        self.assertNotIn('password', resp.get_json())


# ======================================================================
# USERS
# ======================================================================

class TestUserCreation(BaseTestCase):

    def test_admin_creates_user_success(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.create_user_via_api(admin_token)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['email'], 'john@example.com')
        self.assertNotIn('password', data)

    def test_no_token_returns_401(self):
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "J", "last_name": "D",
                               "email": "j@t.com", "password": "p"})
        self.assertEqual(resp.status_code, 401)

    def test_regular_user_token_returns_403(self):
        _, user_token = self.create_regular_user_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "J", "last_name": "D",
                               "email": "j2@t.com", "password": "p"},
                              headers=self.auth_header(user_token))
        self.assertEqual(resp.status_code, 403)

    def test_duplicate_email_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        self.create_user_via_api(admin_token)
        resp = self.create_user_via_api(admin_token)
        self.assertEqual(resp.status_code, 400)

    def test_missing_first_name_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"last_name": "D", "email": "x@t.com", "password": "p"},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_missing_last_name_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "J", "email": "x@t.com", "password": "p"},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_missing_email_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "J", "last_name": "D", "password": "p"},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_missing_password_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "J", "last_name": "D", "email": "x@t.com"},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_invalid_email_format_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "J", "last_name": "D",
                               "email": "not-an-email", "password": "p"},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_empty_first_name_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "   ", "last_name": "D",
                               "email": "x@t.com", "password": "p"},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_response_never_contains_password(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.create_user_via_api(admin_token)
        self.assertNotIn('password', resp.get_json())

    def test_admin_can_create_another_admin(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/users/',
                              {"first_name": "A", "last_name": "B",
                               "email": "admin2@t.com", "password": "p",
                               "is_admin": True},
                              headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 201)


class TestUserRetrieval(BaseTestCase):

    def test_get_all_users_empty(self):
        resp = self.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_all_users_returns_list(self):
        _, admin_token = self.create_admin_and_token()
        self.create_user_via_api(admin_token)
        resp = self.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertGreaterEqual(len(resp.get_json()), 1)

    def test_get_all_users_no_password_exposed(self):
        _, admin_token = self.create_admin_and_token()
        self.create_user_via_api(admin_token)
        for user in self.get('/api/v1/users/').get_json():
            self.assertNotIn('password', user)

    def test_get_user_by_id_success(self):
        user_id, _ = self.create_regular_user_and_token()
        resp = self.get(f'/api/v1/users/{user_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['id'], user_id)
        self.assertIn('first_name', data)
        self.assertIn('email', data)
        self.assertNotIn('password', data)

    def test_get_user_nonexistent_returns_404(self):
        resp = self.get('/api/v1/users/00000000-0000-0000-0000-000000000000')
        self.assertEqual(resp.status_code, 404)

    def test_get_user_invalid_id_returns_404(self):
        resp = self.get('/api/v1/users/not-a-real-id')
        self.assertEqual(resp.status_code, 404)

    def test_count_grows_after_creations(self):
        _, admin_token = self.create_admin_and_token()
        initial = len(self.get('/api/v1/users/').get_json())
        self.create_user_via_api(admin_token, email="u1@t.com")
        self.create_user_via_api(admin_token, email="u2@t.com")
        final = len(self.get('/api/v1/users/').get_json())
        self.assertEqual(final, initial + 2)

    def test_get_all_users_is_public(self):
        resp = self.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)


class TestUserUpdate(BaseTestCase):

    def test_user_updates_own_name(self):
        user_id, token = self.create_regular_user_and_token()
        resp = self.put_json(f'/api/v1/users/{user_id}',
                             {"first_name": "Updated", "last_name": "Name"},
                             headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['first_name'], 'Updated')
        self.assertEqual(resp.get_json()['last_name'], 'Name')

    def test_user_cannot_change_own_email(self):
        user_id, token = self.create_regular_user_and_token()
        resp = self.put_json(f'/api/v1/users/{user_id}',
                             {"email": "new@t.com"},
                             headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 400)

    def test_user_cannot_change_own_password(self):
        user_id, token = self.create_regular_user_and_token()
        resp = self.put_json(f'/api/v1/users/{user_id}',
                             {"password": "newpass"},
                             headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 400)

    def test_user_cannot_update_another_user(self):
        _, token_a = self.create_regular_user_and_token(email="a@t.com")
        user_b_id, _ = self.create_regular_user_and_token(email="b@t.com")
        resp = self.put_json(f'/api/v1/users/{user_b_id}',
                             {"first_name": "Hacked"},
                             headers=self.auth_header(token_a))
        self.assertEqual(resp.status_code, 403)

    def test_no_token_returns_401(self):
        user_id, _ = self.create_regular_user_and_token()
        resp = self.put_json(f'/api/v1/users/{user_id}', {"first_name": "X"})
        self.assertEqual(resp.status_code, 401)

    def test_admin_can_update_any_email(self):
        _, admin_token = self.create_admin_and_token()
        user_id, _ = self.create_regular_user_and_token(email="target@t.com")
        resp = self.put_json(f'/api/v1/users/{user_id}',
                             {"email": "new@t.com"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['email'], 'new@t.com')

    def test_admin_can_update_any_password(self):
        _, admin_token = self.create_admin_and_token()
        user_id, _ = self.create_regular_user_and_token(email="target@t.com")
        resp = self.put_json(f'/api/v1/users/{user_id}',
                             {"password": "newpassword"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_admin_updates_own_account(self):
        admin_id, admin_token = self.create_admin_and_token()
        resp = self.put_json(f'/api/v1/users/{admin_id}',
                             {"first_name": "SuperAdmin"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_update_nonexistent_user_returns_404(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.put_json('/api/v1/users/00000000-0000-0000-0000-000000000000',
                             {"first_name": "X"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 404)

    def test_update_duplicate_email_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        self.create_user_via_api(admin_token, email="first@t.com")
        user2_id, _ = self.create_regular_user_and_token(email="second@t.com")
        resp = self.put_json(f'/api/v1/users/{user2_id}',
                             {"email": "first@t.com"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_update_response_no_password(self):
        user_id, token = self.create_regular_user_and_token()
        resp = self.put_json(f'/api/v1/users/{user_id}',
                             {"first_name": "X", "last_name": "Y"},
                             headers=self.auth_header(token))
        self.assertNotIn('password', resp.get_json())


# ======================================================================
# AMENITIES
# ======================================================================

class TestAmenityCreation(BaseTestCase):

    def test_admin_creates_amenity_success(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.create_amenity(admin_token, "WiFi")
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'WiFi')

    def test_no_token_returns_401(self):
        resp = self.post_json('/api/v1/amenities/', {"name": "Pool"})
        self.assertEqual(resp.status_code, 401)

    def test_regular_user_returns_403(self):
        _, user_token = self.create_regular_user_and_token()
        resp = self.post_json('/api/v1/amenities/', {"name": "Pool"},
                               headers=self.auth_header(user_token))
        self.assertEqual(resp.status_code, 403)

    def test_duplicate_name_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        self.create_amenity(admin_token, "Pool")
        resp = self.post_json('/api/v1/amenities/', {"name": "Pool"},
                               headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_empty_name_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/amenities/', {"name": ""},
                               headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_whitespace_name_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/amenities/', {"name": "   "},
                               headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_missing_name_field_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.post_json('/api/v1/amenities/', {},
                               headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)

    def test_multiple_amenities_have_unique_ids(self):
        _, admin_token = self.create_admin_and_token()
        ids = [self.create_amenity(admin_token, name).get_json()['id']
               for name in ["WiFi", "Pool", "Gym", "Parking"]]
        self.assertEqual(len(set(ids)), 4)


class TestAmenityRetrieval(BaseTestCase):

    def test_get_all_amenities_empty(self):
        resp = self.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_all_amenities_returns_list(self):
        _, admin_token = self.create_admin_and_token()
        self.create_amenity(admin_token, "WiFi")
        self.create_amenity(admin_token, "Pool")
        resp = self.get('/api/v1/amenities/')
        self.assertEqual(len(resp.get_json()), 2)

    def test_get_amenity_by_id_success(self):
        _, admin_token = self.create_admin_and_token()
        amenity_id = self.create_amenity(admin_token, "Parking").get_json()['id']
        resp = self.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['id'], amenity_id)
        self.assertEqual(data['name'], 'Parking')

    def test_get_amenity_nonexistent_returns_404(self):
        resp = self.get('/api/v1/amenities/00000000-0000-0000-0000-000000000000')
        self.assertEqual(resp.status_code, 404)

    def test_get_all_amenities_is_public(self):
        resp = self.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)


class TestAmenityUpdate(BaseTestCase):

    def test_admin_updates_amenity(self):
        _, admin_token = self.create_admin_and_token()
        amenity_id = self.create_amenity(admin_token, "Old").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{amenity_id}',
                             {"name": "New Name"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'New Name')

    def test_regular_user_returns_403(self):
        _, admin_token = self.create_admin_and_token()
        _, user_token = self.create_regular_user_and_token()
        amenity_id = self.create_amenity(admin_token, "WiFi").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{amenity_id}',
                             {"name": "Hacked"},
                             headers=self.auth_header(user_token))
        self.assertEqual(resp.status_code, 403)

    def test_no_token_returns_401(self):
        _, admin_token = self.create_admin_and_token()
        amenity_id = self.create_amenity(admin_token, "WiFi").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{amenity_id}', {"name": "X"})
        self.assertEqual(resp.status_code, 401)

    def test_duplicate_name_on_update_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        h = self.auth_header(admin_token)
        self.create_amenity(admin_token, "WiFi")
        a2_id = self.create_amenity(admin_token, "Pool").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{a2_id}',
                             {"name": "WiFi"}, headers=h)
        self.assertEqual(resp.status_code, 400)

    def test_update_nonexistent_returns_404(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.put_json('/api/v1/amenities/00000000-0000-0000-0000-000000000000',
                             {"name": "X"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 404)

    def test_update_same_name_succeeds(self):
        _, admin_token = self.create_admin_and_token()
        amenity_id = self.create_amenity(admin_token, "WiFi").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{amenity_id}',
                             {"name": "WiFi"},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_empty_name_on_update_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        amenity_id = self.create_amenity(admin_token, "WiFi").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{amenity_id}',
                             {"name": ""},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 400)


# ======================================================================
# PLACES
# ======================================================================

class TestPlaceCreation(BaseTestCase):

    def test_create_place_success(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertIn('owner', data)
        self.assertEqual(data['owner']['id'], owner_id)
        self.assertIn('amenities', data)

    def test_create_place_with_amenities(self):
        _, admin_token = self.create_admin_and_token()
        owner_id, owner_token = self.create_regular_user_and_token()
        a1 = self.create_amenity(admin_token, "WiFi").get_json()['id']
        a2 = self.create_amenity(admin_token, "Pool").get_json()['id']
        resp = self.create_place(owner_token, owner_id, amenity_ids=[a1, a2])
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(len(resp.get_json()['amenities']), 2)

    def test_no_token_returns_401(self):
        owner_id, _ = self.create_regular_user_and_token()
        resp = self.post_json('/api/v1/places/',
                              {"title": "T", "price": 10.0,
                               "latitude": 0, "longitude": 0,
                               "owner_id": owner_id, "amenities": []})
        self.assertEqual(resp.status_code, 401)

    def test_owner_id_mismatch_returns_403(self):
        owner_id, _ = self.create_regular_user_and_token(email="o@t.com")
        _, other_token = self.create_regular_user_and_token(email="x@t.com")
        resp = self.create_place(other_token, owner_id)
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_create_for_anyone(self):
        _, admin_token = self.create_admin_and_token()
        owner_id, _ = self.create_regular_user_and_token()
        resp = self.create_place(admin_token, owner_id)
        self.assertEqual(resp.status_code, 201)

    def test_nonexistent_owner_returns_400(self):
        _, admin_token = self.create_admin_and_token()
        resp = self.create_place(admin_token,
                                  "00000000-0000-0000-0000-000000000000")
        self.assertEqual(resp.status_code, 400)

    def test_negative_price_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, price=-1.0)
        self.assertEqual(resp.status_code, 400)

    def test_zero_price_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, price=0)
        self.assertEqual(resp.status_code, 400)

    def test_latitude_above_90_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, latitude=91.0)
        self.assertEqual(resp.status_code, 400)

    def test_latitude_below_minus90_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, latitude=-91.0)
        self.assertEqual(resp.status_code, 400)

    def test_longitude_above_180_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, longitude=181.0)
        self.assertEqual(resp.status_code, 400)

    def test_longitude_below_minus180_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, longitude=-181.0)
        self.assertEqual(resp.status_code, 400)

    def test_latitude_boundary_90_succeeds(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        self.assertEqual(self.create_place(owner_token, owner_id,
                                            latitude=90.0).status_code, 201)

    def test_latitude_boundary_minus90_succeeds(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        self.assertEqual(self.create_place(owner_token, owner_id,
                                            latitude=-90.0).status_code, 201)

    def test_longitude_boundary_180_succeeds(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        self.assertEqual(self.create_place(owner_token, owner_id,
                                            longitude=180.0).status_code, 201)

    def test_longitude_boundary_minus180_succeeds(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        self.assertEqual(self.create_place(owner_token, owner_id,
                                            longitude=-180.0).status_code, 201)

    def test_missing_title_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.post_json('/api/v1/places/',
                              {"price": 50.0, "latitude": 0.0,
                               "longitude": 0.0, "owner_id": owner_id,
                               "amenities": []},
                              headers=self.auth_header(owner_token))
        self.assertEqual(resp.status_code, 400)

    def test_empty_title_returns_400(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        resp = self.create_place(owner_token, owner_id, title="")
        self.assertEqual(resp.status_code, 400)

    def test_response_contains_owner_without_password(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        place = self.create_place(owner_token, owner_id).get_json()
        self.assertNotIn('password', place['owner'])


class TestPlaceRetrieval(BaseTestCase):

    def test_get_all_places_empty(self):
        resp = self.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_all_places_after_creation(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        self.create_place(owner_token, owner_id)
        self.assertEqual(len(self.get('/api/v1/places/').get_json()), 1)

    def test_get_place_by_id_success(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        place_id = self.create_place(owner_token, owner_id).get_json()['id']
        resp = self.get(f'/api/v1/places/{place_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], place_id)

    def test_get_place_nonexistent_returns_404(self):
        resp = self.get('/api/v1/places/00000000-0000-0000-0000-000000000000')
        self.assertEqual(resp.status_code, 404)

    def test_place_response_has_required_fields(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        place = self.create_place(owner_token, owner_id).get_json()
        for key in ('id', 'title', 'description', 'price',
                    'latitude', 'longitude', 'owner', 'amenities'):
            self.assertIn(key, place)

    def test_owner_details_in_place_response(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        place_id = self.create_place(owner_token, owner_id).get_json()['id']
        owner_data = self.get(f'/api/v1/places/{place_id}').get_json()['owner']
        self.assertIn('id', owner_data)
        self.assertIn('first_name', owner_data)
        self.assertIn('email', owner_data)
        self.assertNotIn('password', owner_data)

    def test_get_all_places_is_public(self):
        self.assertEqual(self.get('/api/v1/places/').status_code, 200)


class TestPlaceUpdate(BaseTestCase):

    def test_owner_updates_place(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.put_json(f'/api/v1/places/{place_id}',
                             {"title": "Updated", "price": 150.0,
                              "latitude": 45.0, "longitude": 10.0},
                             headers=self.auth_header(owner_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['title'], 'Updated')

    def test_non_owner_returns_403(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        _, other_token = self.create_regular_user_and_token(email="x@t.com")
        resp = self.put_json(f'/api/v1/places/{place_id}',
                             {"title": "Stolen"},
                             headers=self.auth_header(other_token))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_update_any_place(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        _, admin_token = self.create_admin_and_token()
        resp = self.put_json(f'/api/v1/places/{place_id}',
                             {"title": "Admin Override", "price": 999.0,
                              "latitude": 0.0, "longitude": 0.0},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_no_token_returns_401(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.put_json(f'/api/v1/places/{place_id}', {"title": "X"})
        self.assertEqual(resp.status_code, 401)

    def test_update_nonexistent_returns_404(self):
        _, token = self.create_regular_user_and_token()
        resp = self.put_json('/api/v1/places/00000000-0000-0000-0000-000000000000',
                             {"title": "X"},
                             headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 404)

    def test_update_invalid_price_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.put_json(f'/api/v1/places/{place_id}',
                             {"title": "T", "price": -5.0,
                              "latitude": 0, "longitude": 0},
                             headers=self.auth_header(owner_token))
        self.assertEqual(resp.status_code, 400)

    def test_put_cannot_change_owner_id(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.put_json(f'/api/v1/places/{place_id}',
                             {"title": "Updated", "price": 50.0,
                              "latitude": 0, "longitude": 0,
                              "owner_id": "fake-owner-id"},
                             headers=self.auth_header(owner_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['owner']['id'], owner_id)


class TestPlaceDeletion(BaseTestCase):

    def test_owner_deletes_place(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.delete(f'/api/v1/places/{place_id}',
                            headers=self.auth_header(owner_token))
        self.assertEqual(resp.status_code, 200)

    def test_deleted_place_returns_404(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        self.delete(f'/api/v1/places/{place_id}',
                     headers=self.auth_header(owner_token))
        self.assertEqual(self.get(f'/api/v1/places/{place_id}').status_code, 404)

    def test_non_owner_delete_returns_403(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        _, other_token = self.create_regular_user_and_token(email="x@t.com")
        resp = self.delete(f'/api/v1/places/{place_id}',
                            headers=self.auth_header(other_token))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_delete_any_place(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        _, admin_token = self.create_admin_and_token()
        resp = self.delete(f'/api/v1/places/{place_id}',
                            headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_no_token_returns_401(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        self.assertEqual(
            self.delete(f'/api/v1/places/{place_id}').status_code, 401)

    def test_delete_nonexistent_returns_404(self):
        _, token = self.create_regular_user_and_token()
        resp = self.delete('/api/v1/places/00000000-0000-0000-0000-000000000000',
                            headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 404)


class TestPlaceReviews(BaseTestCase):

    def test_get_reviews_for_place_empty(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.get(f'/api/v1/places/{place_id}/reviews')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_reviews_for_place_with_data(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        r1_id, r1_token = self.create_regular_user_and_token(email="r1@t.com")
        r2_id, r2_token = self.create_regular_user_and_token(email="r2@t.com")
        self.create_review(r1_token, r1_id, place_id)
        self.create_review(r2_token, r2_id, place_id)
        resp = self.get(f'/api/v1/places/{place_id}/reviews')
        self.assertEqual(len(resp.get_json()), 2)

    def test_get_reviews_nonexistent_place_returns_404(self):
        resp = self.get('/api/v1/places/00000000-0000-0000-0000-000000000000/reviews')
        self.assertEqual(resp.status_code, 404)

    def test_place_reviews_is_public(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        self.assertEqual(
            self.get(f'/api/v1/places/{place_id}/reviews').status_code, 200)


# ======================================================================
# REVIEWS
# ======================================================================

class TestReviewCreation(BaseTestCase):

    def test_create_review_success(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.create_review(reviewer_token, reviewer_id, place_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['text'], 'Great!')
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['user_id'], reviewer_id)
        self.assertEqual(data['place_id'], place_id)

    def test_no_token_returns_401(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, _ = self.create_regular_user_and_token(email="r@t.com")
        resp = self.post_json('/api/v1/reviews/',
                              {"text": "Nice", "rating": 4,
                               "user_id": reviewer_id, "place_id": place_id})
        self.assertEqual(resp.status_code, 401)

    def test_review_own_place_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        resp = self.create_review(owner_token, owner_id, place_id)
        self.assertEqual(resp.status_code, 400)
        self.assertIn('own place', resp.get_json().get('error', '').lower())

    def test_duplicate_review_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        self.create_review(reviewer_token, reviewer_id, place_id)
        resp = self.create_review(reviewer_token, reviewer_id, place_id,
                                   text="Second")
        self.assertEqual(resp.status_code, 400)
        self.assertIn('already', resp.get_json().get('error', '').lower())

    def test_user_id_mismatch_returns_403(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.post_json('/api/v1/reviews/',
                              {"text": "Spoof", "rating": 3,
                               "user_id": owner_id, "place_id": place_id},
                              headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 403)

    def test_nonexistent_place_returns_404(self):
        reviewer_id, reviewer_token = self.create_regular_user_and_token()
        resp = self.post_json('/api/v1/reviews/',
                              {"text": "Nice", "rating": 4,
                               "user_id": reviewer_id,
                               "place_id": "00000000-0000-0000-0000-000000000000"},
                              headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 404)

    def test_rating_above_5_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.create_review(reviewer_token, reviewer_id, place_id, rating=6)
        self.assertEqual(resp.status_code, 400)

    def test_rating_below_1_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.create_review(reviewer_token, reviewer_id, place_id, rating=0)
        self.assertEqual(resp.status_code, 400)

    def test_rating_boundary_1_succeeds(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        self.assertEqual(
            self.create_review(reviewer_token, reviewer_id, place_id,
                                rating=1).status_code, 201)

    def test_rating_boundary_5_succeeds(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        self.assertEqual(
            self.create_review(reviewer_token, reviewer_id, place_id,
                                rating=5).status_code, 201)

    def test_missing_text_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.post_json('/api/v1/reviews/',
                              {"rating": 4, "user_id": reviewer_id,
                               "place_id": place_id},
                              headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 400)

    def test_empty_text_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.create_review(reviewer_token, reviewer_id, place_id, text="  ")
        self.assertEqual(resp.status_code, 400)

    def test_missing_rating_returns_400(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        resp = self.post_json('/api/v1/reviews/',
                              {"text": "OK", "user_id": reviewer_id,
                               "place_id": place_id},
                              headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 400)

    def test_multiple_users_can_review_same_place(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        for i in range(4):
            rid, rtok = self.create_regular_user_and_token(email=f"r{i}@t.com")
            self.assertEqual(
                self.create_review(rtok, rid, place_id,
                                    text=f"Review {i}",
                                    rating=i + 1).status_code, 201)
        reviews = self.get(f'/api/v1/places/{place_id}/reviews').get_json()
        self.assertEqual(len(reviews), 4)


class TestReviewRetrieval(BaseTestCase):

    def test_get_all_reviews_empty(self):
        resp = self.get('/api/v1/reviews/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_all_reviews_after_creation(self):
        (_, _, reviewer_id, reviewer_token,
         place_id, _) = self.setup_review_scenario()
        self.assertEqual(len(self.get('/api/v1/reviews/').get_json()), 1)

    def test_get_review_by_id_success(self):
        (_, _, reviewer_id, reviewer_token,
         place_id, review_id) = self.setup_review_scenario()
        resp = self.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data['id'], review_id)
        self.assertEqual(data['user_id'], reviewer_id)
        self.assertEqual(data['place_id'], place_id)

    def test_get_review_nonexistent_returns_404(self):
        resp = self.get('/api/v1/reviews/00000000-0000-0000-0000-000000000000')
        self.assertEqual(resp.status_code, 404)

    def test_get_reviews_is_public(self):
        self.assertEqual(self.get('/api/v1/reviews/').status_code, 200)


class TestReviewUpdate(BaseTestCase):

    def test_author_updates_text_and_rating(self):
        (_, _, _, reviewer_token,
         _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"text": "Updated text", "rating": 3},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['text'], 'Updated text')
        self.assertEqual(resp.get_json()['rating'], 3)

    def test_author_updates_only_text(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"text": "New text only"},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 200)

    def test_author_updates_only_rating(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"rating": 2},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['rating'], 2)

    def test_non_author_returns_403(self):
        (_, _, _, _, _, review_id) = self.setup_review_scenario()
        _, other_token = self.create_regular_user_and_token(email="x@t.com")
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"text": "Unauthorized"},
                             headers=self.auth_header(other_token))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_update_any_review(self):
        (_, _, _, _, _, review_id) = self.setup_review_scenario()
        _, admin_token = self.create_admin_and_token()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"text": "Admin edit", "rating": 1},
                             headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_no_token_returns_401(self):
        (_, _, _, _, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"text": "No auth"})
        self.assertEqual(resp.status_code, 401)

    def test_cannot_change_place_id_returns_400(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"place_id": "other-place-id"},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 400)

    def test_cannot_change_user_id_returns_400(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"user_id": "other-user-id"},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 400)

    def test_update_invalid_rating_returns_400(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"rating": 10},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 400)

    def test_update_empty_text_returns_400(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.put_json(f'/api/v1/reviews/{review_id}',
                             {"text": ""},
                             headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 400)

    def test_update_nonexistent_review_returns_404(self):
        _, token = self.create_regular_user_and_token()
        resp = self.put_json(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000',
            {"text": "X", "rating": 3},
            headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 404)


class TestReviewDeletion(BaseTestCase):

    def test_author_deletes_review(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        resp = self.delete(f'/api/v1/reviews/{review_id}',
                            headers=self.auth_header(reviewer_token))
        self.assertEqual(resp.status_code, 200)

    def test_deleted_review_returns_404(self):
        (_, _, _, reviewer_token, _, review_id) = self.setup_review_scenario()
        self.delete(f'/api/v1/reviews/{review_id}',
                     headers=self.auth_header(reviewer_token))
        self.assertEqual(self.get(f'/api/v1/reviews/{review_id}').status_code, 404)

    def test_non_author_delete_returns_403(self):
        (_, _, _, _, _, review_id) = self.setup_review_scenario()
        _, other_token = self.create_regular_user_and_token(email="x@t.com")
        resp = self.delete(f'/api/v1/reviews/{review_id}',
                            headers=self.auth_header(other_token))
        self.assertEqual(resp.status_code, 403)

    def test_admin_can_delete_any_review(self):
        (_, _, _, _, _, review_id) = self.setup_review_scenario()
        _, admin_token = self.create_admin_and_token()
        resp = self.delete(f'/api/v1/reviews/{review_id}',
                            headers=self.auth_header(admin_token))
        self.assertEqual(resp.status_code, 200)

    def test_no_token_returns_401(self):
        (_, _, _, _, _, review_id) = self.setup_review_scenario()
        self.assertEqual(
            self.delete(f'/api/v1/reviews/{review_id}').status_code, 401)

    def test_delete_nonexistent_returns_404(self):
        _, token = self.create_regular_user_and_token()
        resp = self.delete(
            '/api/v1/reviews/00000000-0000-0000-0000-000000000000',
            headers=self.auth_header(token))
        self.assertEqual(resp.status_code, 404)

    def test_review_count_decreases_after_deletion(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        r1_id, r1_token = self.create_regular_user_and_token(email="r1@t.com")
        r2_id, r2_token = self.create_regular_user_and_token(email="r2@t.com")
        review1_id = self.create_review(
            r1_token, r1_id, place_id).get_json()['id']
        self.create_review(r2_token, r2_id, place_id)
        self.assertEqual(len(self.get('/api/v1/reviews/').get_json()), 2)
        self.delete(f'/api/v1/reviews/{review1_id}',
                     headers=self.auth_header(r1_token))
        self.assertEqual(len(self.get('/api/v1/reviews/').get_json()), 1)


# ======================================================================
# INTEGRATION
# ======================================================================

class TestIntegration(BaseTestCase):

    def test_full_lifecycle(self):
        _, admin_token = self.create_admin_and_token()
        owner = self.create_user_via_api(
            admin_token, email="owner@ex.com",
            first_name="Owner", last_name="Test").get_json()
        amenity_id = self.create_amenity(admin_token, "Gym").get_json()['id']
        owner_token = self.get_token("owner@ex.com", "pass123")
        place = self.create_place(owner_token, owner['id'],
                                   amenity_ids=[amenity_id]).get_json()
        self.assertEqual(len(place['amenities']), 1)

        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="rev@ex.com")
        review = self.create_review(reviewer_token, reviewer_id,
                                     place['id'], text="Excellent!",
                                     rating=5).get_json()
        self.assertIn('id', review)

        reviews = self.get(f"/api/v1/places/{place['id']}/reviews").get_json()
        self.assertEqual(len(reviews), 1)

        updated = self.put_json(f"/api/v1/reviews/{review['id']}",
                                {"text": "Still great", "rating": 4},
                                headers=self.auth_header(reviewer_token)).get_json()
        self.assertEqual(updated['rating'], 4)

        del_resp = self.delete(f"/api/v1/reviews/{review['id']}",
                                headers=self.auth_header(reviewer_token))
        self.assertEqual(del_resp.status_code, 200)
        self.assertEqual(
            self.get(f"/api/v1/reviews/{review['id']}").status_code, 404)

    def test_delete_place_removes_reviews(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        review_id = self.create_review(
            reviewer_token, reviewer_id, place_id).get_json()['id']
        self.delete(f'/api/v1/places/{place_id}',
                     headers=self.auth_header(owner_token))
        self.assertEqual(self.get(f'/api/v1/reviews/{review_id}').status_code, 404)

    def test_place_response_structure_complete(self):
        _, admin_token = self.create_admin_and_token()
        owner_id, owner_token = self.create_regular_user_and_token()
        amenity_id = self.create_amenity(admin_token, "WiFi").get_json()['id']
        place = self.create_place(owner_token, owner_id,
                                   amenity_ids=[amenity_id]).get_json()
        for key in ('id', 'title', 'description', 'price',
                    'latitude', 'longitude', 'owner', 'amenities'):
            self.assertIn(key, place)
        self.assertNotIn('password', place['owner'])
        self.assertEqual(place['amenities'][0]['name'], 'WiFi')

    def test_admin_can_manage_all_resources(self):
        _, admin_token = self.create_admin_and_token()
        ah = self.auth_header(admin_token)
        user = self.create_user_via_api(
            admin_token, email="u@ex.com").get_json()
        amenity_id = self.create_amenity(admin_token, "Pool").get_json()['id']
        user_token = self.get_token("u@ex.com", "pass123")
        place_id = self.create_place(user_token, user['id']).get_json()['id']
        self.assertEqual(
            self.put_json(f'/api/v1/places/{place_id}',
                          {"title": "Admin Modified", "price": 1.0,
                           "latitude": 0, "longitude": 0},
                          headers=ah).status_code, 200)
        self.assertEqual(
            self.put_json(f'/api/v1/amenities/{amenity_id}',
                          {"name": "Updated Pool"}, headers=ah).status_code, 200)
        self.assertEqual(
            self.delete(f'/api/v1/places/{place_id}',
                         headers=ah).status_code, 200)

    def test_user_count_after_multiple_creations(self):
        _, admin_token = self.create_admin_and_token()
        for i in range(5):
            self.create_user_via_api(admin_token, email=f"user{i}@ex.com",
                                      first_name=f"U{i}", last_name="T")
        # 5 créés + 1 admin
        self.assertEqual(len(self.get('/api/v1/users/').get_json()), 6)

    def test_different_places_have_independent_reviews(self):
        owner_id, owner_token = self.create_regular_user_and_token(email="o@t.com")
        place1_id = self.create_place(owner_token, owner_id,
                                       title="Place 1").get_json()['id']
        place2_id = self.create_place(owner_token, owner_id,
                                       title="Place 2").get_json()['id']
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        self.create_review(reviewer_token, reviewer_id, place1_id)
        self.assertEqual(
            len(self.get(f'/api/v1/places/{place1_id}/reviews').get_json()), 1)
        self.assertEqual(
            len(self.get(f'/api/v1/places/{place2_id}/reviews').get_json()), 0)

    def test_token_works_for_all_protected_endpoints(self):
        owner_id, owner_token = self.create_regular_user_and_token()
        h = self.auth_header(owner_token)
        place = self.create_place(owner_token, owner_id).get_json()
        self.assertEqual(
            self.put_json(f"/api/v1/places/{place['id']}",
                          {"title": "T", "price": 10.0,
                           "latitude": 0, "longitude": 0},
                          headers=h).status_code, 200)
        self.assertEqual(
            self.delete(f"/api/v1/places/{place['id']}",
                         headers=h).status_code, 200)

    def test_review_appears_in_place_reviews_and_global_reviews(self):
        owner_id, owner_token, place_id = self.setup_owner_and_place()
        reviewer_id, reviewer_token = self.create_regular_user_and_token(
            email="r@t.com")
        review_id = self.create_review(
            reviewer_token, reviewer_id, place_id).get_json()['id']
        all_review_ids = [r['id'] for r in self.get('/api/v1/reviews/').get_json()]
        place_review_ids = [r['id'] for r in
                             self.get(f'/api/v1/places/{place_id}/reviews').get_json()]
        self.assertIn(review_id, all_review_ids)
        self.assertIn(review_id, place_review_ids)


if __name__ == '__main__':
    unittest.main(verbosity=2)
