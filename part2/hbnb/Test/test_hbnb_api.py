"""
HBnB API - Test Suite Complet
Tests unitaires pour les endpoints: Users, Amenities, Places, Reviews
Utilisation: python -m pytest test_hbnb_api.py -v
          ou: python -m unittest test_hbnb_api -v
"""

import unittest
import json
import sys
import os

# Ajoute le dossier parent au path pour l'import de l'app
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app


class BaseTestCase(unittest.TestCase):
    """Classe de base avec setup/teardown commun à tous les tests."""

    def setUp(self):
        """Crée une instance de l'app en mode test avant chaque test."""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()

    def post_json(self, url, data):
        return self.client.post(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

    def put_json(self, url, data):
        return self.client.put(
            url,
            data=json.dumps(data),
            content_type='application/json'
        )

    # ------------------------------------------------------------------ #
    # Helpers de création rapide (réutilisés dans plusieurs test classes) #
    # ------------------------------------------------------------------ #

    def create_user(self, first_name="John", last_name="Doe",
                    email="john.doe@example.com", password="secret"):
        return self.post_json('/api/v1/users/', {
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "password": password
        })

    def create_amenity(self, name="WiFi"):
        return self.post_json('/api/v1/amenities/', {"name": name})

    def create_place(self, owner_id, amenity_ids=None, **kwargs):
        data = {
            "title": kwargs.get("title", "Nice Place"),
            "description": kwargs.get("description", "A great spot"),
            "price": kwargs.get("price", 99.9),
            "latitude": kwargs.get("latitude", 48.8566),
            "longitude": kwargs.get("longitude", 2.3522),
            "owner_id": owner_id,
            "amenities": amenity_ids or []
        }
        return self.post_json('/api/v1/places/', data)

    def create_review(self, user_id, place_id, text="Great!", rating=5):
        return self.post_json('/api/v1/reviews/', {
            "text": text,
            "rating": rating,
            "user_id": user_id,
            "place_id": place_id
        })


# ====================================================================== #
#                           USERS TESTS                                   #
# ====================================================================== #

class TestUserCreation(BaseTestCase):
    """Tests de création d'utilisateur - POST /api/v1/users/"""

    def test_create_user_success(self):
        """Création d'un utilisateur valide → 201."""
        resp = self.create_user()
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['first_name'], 'John')
        self.assertEqual(data['last_name'], 'Doe')
        self.assertEqual(data['email'], 'john.doe@example.com')

    def test_create_user_duplicate_email(self):
        """Doublon d'email → 400."""
        self.create_user()
        resp = self.create_user()  # même email
        self.assertEqual(resp.status_code, 400)
        self.assertIn('error', resp.get_json())

    def test_create_user_missing_first_name(self):
        """Champ first_name manquant → 400."""
        resp = self.post_json('/api/v1/users/', {
            "last_name": "Doe",
            "email": "nodoe@example.com",
            "password": "secret"
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_user_missing_last_name(self):
        """Champ last_name manquant → 400."""
        resp = self.post_json('/api/v1/users/', {
            "first_name": "Jane",
            "email": "jane@example.com",
            "password": "secret"
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_user_missing_email(self):
        """Champ email manquant → 400."""
        resp = self.post_json('/api/v1/users/', {
            "first_name": "Jane",
            "last_name": "Doe",
            "password": "secret"
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_user_empty_payload(self):
        """Payload vide → 400."""
        resp = self.post_json('/api/v1/users/', {})
        self.assertEqual(resp.status_code, 400)


class TestUserRetrieval(BaseTestCase):
    """Tests de récupération d'utilisateurs."""

    def test_get_all_users_empty(self):
        """Liste vide au départ → 200 + liste vide."""
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_all_users_after_creation(self):
        """Après création → liste non vide."""
        self.create_user()
        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 1)

    def test_get_user_by_id_success(self):
        """Récupération par ID valide → 200."""
        user_id = self.create_user().get_json()['id']
        resp = self.client.get(f'/api/v1/users/{user_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], user_id)

    def test_get_user_by_invalid_id(self):
        """ID inexistant → 404."""
        resp = self.client.get('/api/v1/users/nonexistent-id')
        self.assertEqual(resp.status_code, 404)


class TestUserUpdate(BaseTestCase):
    """Tests de mise à jour d'utilisateur - PUT /api/v1/users/<id>"""

    def test_update_user_success(self):
        """Mise à jour valide → 200."""
        user_id = self.create_user().get_json()['id']
        resp = self.put_json(f'/api/v1/users/{user_id}', {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "password": "newpass"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['first_name'], 'Updated')

    def test_update_user_not_found(self):
        """ID inexistant → 404."""
        resp = self.put_json('/api/v1/users/bad-id', {
            "first_name": "X",
            "last_name": "Y",
            "email": "x@example.com",
            "password": "p"
        })
        self.assertEqual(resp.status_code, 404)

    def test_update_user_duplicate_email(self):
        """Changement vers un email déjà pris → 400."""
        self.create_user(email="first@example.com")
        user2_id = self.create_user(
            email="second@example.com", first_name="Jane"
        ).get_json()['id']
        resp = self.put_json(f'/api/v1/users/{user2_id}', {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "first@example.com",
            "password": "secret"
        })
        self.assertEqual(resp.status_code, 400)


# ====================================================================== #
#                         AMENITIES TESTS                                  #
# ====================================================================== #

class TestAmenityCreation(BaseTestCase):
    """Tests de création d'amenité - POST /api/v1/amenities/"""

    def test_create_amenity_success(self):
        """Création valide → 201."""
        resp = self.create_amenity("WiFi")
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'WiFi')

    def test_create_amenity_duplicate(self):
        """Doublon de nom → 400."""
        self.create_amenity("Pool")
        resp = self.create_amenity("Pool")
        self.assertEqual(resp.status_code, 400)

    def test_create_amenity_missing_name(self):
        """Champ name manquant → 400."""
        resp = self.post_json('/api/v1/amenities/', {})
        self.assertEqual(resp.status_code, 400)


class TestAmenityRetrieval(BaseTestCase):
    """Tests de récupération d'amenités."""

    def test_get_all_amenities_empty(self):
        """Liste vide → 200 + []."""
        resp = self.client.get('/api/v1/amenities/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_amenity_by_id_success(self):
        """Récupération par ID valide → 200."""
        amenity_id = self.create_amenity("Parking").get_json()['id']
        resp = self.client.get(f'/api/v1/amenities/{amenity_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], amenity_id)

    def test_get_amenity_by_invalid_id(self):
        """ID inexistant → 404."""
        resp = self.client.get('/api/v1/amenities/nonexistent-id')
        self.assertEqual(resp.status_code, 404)


class TestAmenityUpdate(BaseTestCase):
    """Tests de mise à jour d'amenité - PUT /api/v1/amenities/<id>"""

    def test_update_amenity_success(self):
        """Mise à jour valide → 200."""
        amenity_id = self.create_amenity("Old Name").get_json()['id']
        resp = self.put_json(f'/api/v1/amenities/{amenity_id}', {
            "name": "New Name"
        })
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['name'], 'New Name')

    def test_update_amenity_not_found(self):
        """ID inexistant → 404."""
        resp = self.put_json('/api/v1/amenities/bad-id', {"name": "X"})
        self.assertEqual(resp.status_code, 404)


# ====================================================================== #
#                           PLACES TESTS                                   #
# ====================================================================== #

class TestPlaceCreation(BaseTestCase):
    """Tests de création de place - POST /api/v1/places/"""

    def test_create_place_success(self):
        """Création valide → 201."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['title'], 'Nice Place')
        self.assertIn('owner', data)
        self.assertEqual(data['owner']['id'], owner_id)

    def test_create_place_with_amenities(self):
        """Création avec amenités → 201, amenités dans la réponse."""
        owner_id = self.create_user().get_json()['id']
        a1 = self.create_amenity("WiFi").get_json()['id']
        a2 = self.create_amenity("Pool").get_json()['id']
        resp = self.create_place(owner_id, amenity_ids=[a1, a2])
        self.assertEqual(resp.status_code, 201)
        amenities = resp.get_json()['amenities']
        self.assertEqual(len(amenities), 2)

    def test_create_place_invalid_owner(self):
        """Owner_id inexistant → 400."""
        resp = self.create_place("nonexistent-owner-id")
        self.assertEqual(resp.status_code, 400)

    def test_create_place_negative_price(self):
        """Prix négatif → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, price=-10.0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_zero_price(self):
        """Prix à zéro → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, price=0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_invalid_latitude_too_high(self):
        """Latitude > 90 → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, latitude=91.0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_invalid_latitude_too_low(self):
        """Latitude < -90 → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, latitude=-91.0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_invalid_longitude_too_high(self):
        """Longitude > 180 → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, longitude=181.0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_invalid_longitude_too_low(self):
        """Longitude < -180 → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, longitude=-181.0)
        self.assertEqual(resp.status_code, 400)

    def test_create_place_boundary_latitude(self):
        """Latitude = 90 (borne max) → 201."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, latitude=90.0)
        self.assertEqual(resp.status_code, 201)

    def test_create_place_boundary_longitude(self):
        """Longitude = -180 (borne min) → 201."""
        owner_id = self.create_user().get_json()['id']
        resp = self.create_place(owner_id, longitude=-180.0)
        self.assertEqual(resp.status_code, 201)

    def test_create_place_missing_title(self):
        """Titre manquant → 400."""
        owner_id = self.create_user().get_json()['id']
        resp = self.post_json('/api/v1/places/', {
            "price": 50.0,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": owner_id,
            "amenities": []
        })
        self.assertEqual(resp.status_code, 400)


class TestPlaceRetrieval(BaseTestCase):
    """Tests de récupération de places."""

    def test_get_all_places_empty(self):
        """Liste vide → 200 + []."""
        resp = self.client.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_place_by_id_success(self):
        """Récupération par ID valide → 200."""
        owner_id = self.create_user().get_json()['id']
        place_id = self.create_place(owner_id).get_json()['id']
        resp = self.client.get(f'/api/v1/places/{place_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], place_id)

    def test_get_place_by_invalid_id(self):
        """ID inexistant → 404."""
        resp = self.client.get('/api/v1/places/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    def test_get_all_places_multiple(self):
        """Plusieurs places → liste complète."""
        owner_id = self.create_user().get_json()['id']
        self.create_place(owner_id, title="Place 1")
        self.create_place(owner_id, title="Place 2")
        resp = self.client.get('/api/v1/places/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)


class TestPlaceUpdate(BaseTestCase):
    """Tests de mise à jour de place - PUT /api/v1/places/<id>"""

    def test_update_place_success(self):
        """Mise à jour valide → 200."""
        owner_id = self.create_user().get_json()['id']
        place_id = self.create_place(owner_id).get_json()['id']
        resp = self.put_json(f'/api/v1/places/{place_id}', {
            "title": "Updated Title",
            "price": 150.0,
            "latitude": 45.0,
            "longitude": 10.0,
            "owner_id": owner_id,
            "amenities": []
        })
        self.assertEqual(resp.status_code, 200)

    def test_update_place_not_found(self):
        """ID inexistant → 404."""
        resp = self.put_json('/api/v1/places/bad-id', {
            "title": "X",
            "price": 10.0,
            "latitude": 0.0,
            "longitude": 0.0,
            "owner_id": "some-id",
            "amenities": []
        })
        self.assertEqual(resp.status_code, 404)


# ====================================================================== #
#                           REVIEWS TESTS                                  #
# ====================================================================== #

class TestReviewCreation(BaseTestCase):
    """Tests de création de review - POST /api/v1/reviews/"""

    def _setup(self):
        user_id = self.create_user().get_json()['id']
        place_id = self.create_place(user_id).get_json()['id']
        return user_id, place_id

    def test_create_review_success(self):
        """Création valide → 201."""
        user_id, place_id = self._setup()
        resp = self.create_review(user_id, place_id)
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertIn('id', data)
        self.assertEqual(data['text'], 'Great!')
        self.assertEqual(data['rating'], 5)
        self.assertEqual(data['user_id'], user_id)
        self.assertEqual(data['place_id'], place_id)

    def test_create_review_invalid_user(self):
        """user_id inexistant → 400."""
        user_id, place_id = self._setup()
        resp = self.create_review("bad-user-id", place_id)
        self.assertEqual(resp.status_code, 400)

    def test_create_review_invalid_place(self):
        """place_id inexistant → 400."""
        user_id, _ = self._setup()
        resp = self.create_review(user_id, "bad-place-id")
        self.assertEqual(resp.status_code, 400)

    def test_create_review_missing_text(self):
        """Texte manquant → 400."""
        user_id, place_id = self._setup()
        resp = self.post_json('/api/v1/reviews/', {
            "rating": 4,
            "user_id": user_id,
            "place_id": place_id
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_review_missing_rating(self):
        """Rating manquant → 400."""
        user_id, place_id = self._setup()
        resp = self.post_json('/api/v1/reviews/', {
            "text": "OK",
            "user_id": user_id,
            "place_id": place_id
        })
        self.assertEqual(resp.status_code, 400)

    def test_create_review_rating_boundary_min(self):
        """Rating = 1 (borne min) → 201."""
        user_id, place_id = self._setup()
        resp = self.create_review(user_id, place_id, rating=1)
        self.assertEqual(resp.status_code, 201)

    def test_create_review_rating_boundary_max(self):
        """Rating = 5 (borne max) → 201."""
        user_id, place_id = self._setup()
        resp = self.create_review(user_id, place_id, rating=5)
        self.assertEqual(resp.status_code, 201)


class TestReviewRetrieval(BaseTestCase):
    """Tests de récupération de reviews."""

    def test_get_all_reviews_empty(self):
        """Liste vide → 200 + []."""
        resp = self.client.get('/api/v1/reviews/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json(), [])

    def test_get_review_by_id_success(self):
        """Récupération par ID valide → 200."""
        user_id = self.create_user().get_json()['id']
        place_id = self.create_place(user_id).get_json()['id']
        review_id = self.create_review(user_id, place_id).get_json()['id']
        resp = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.get_json()['id'], review_id)

    def test_get_review_by_invalid_id(self):
        """ID inexistant → 404."""
        resp = self.client.get('/api/v1/reviews/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    def test_get_reviews_by_place(self):
        """GET /api/v1/places/<id>/reviews → liste des reviews."""
        user_id = self.create_user().get_json()['id']
        place_id = self.create_place(user_id).get_json()['id']
        self.create_review(user_id, place_id, text="Super!")
        self.create_review(user_id, place_id, text="Not bad")
        resp = self.client.get(f'/api/v1/places/{place_id}/reviews')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 2)

    def test_get_reviews_by_invalid_place(self):
        """Place inexistante → 404."""
        resp = self.client.get('/api/v1/places/bad-id/reviews')
        self.assertEqual(resp.status_code, 404)


class TestReviewUpdate(BaseTestCase):
    """Tests de mise à jour de review - PUT /api/v1/reviews/<id>"""

    def test_update_review_success(self):
        """Mise à jour valide → 200."""
        user_id = self.create_user().get_json()['id']
        place_id = self.create_place(user_id).get_json()['id']
        review_id = self.create_review(user_id, place_id).get_json()['id']
        resp = self.put_json(f'/api/v1/reviews/{review_id}', {
            "text": "Updated text",
            "rating": 3,
            "user_id": user_id,
            "place_id": place_id
        })
        self.assertEqual(resp.status_code, 200)

    def test_update_review_not_found(self):
        """ID inexistant → 404."""
        resp = self.put_json('/api/v1/reviews/bad-id', {
            "text": "X",
            "rating": 3,
            "user_id": "u",
            "place_id": "p"
        })
        self.assertEqual(resp.status_code, 404)


class TestReviewDeletion(BaseTestCase):
    """Tests de suppression de review - DELETE /api/v1/reviews/<id>"""

    def test_delete_review_success(self):
        """Suppression valide → 200."""
        user_id = self.create_user().get_json()['id']
        place_id = self.create_place(user_id).get_json()['id']
        review_id = self.create_review(user_id, place_id).get_json()['id']
        resp = self.client.delete(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 200)

    def test_delete_review_not_found(self):
        """ID inexistant → 404."""
        resp = self.client.delete('/api/v1/reviews/nonexistent-id')
        self.assertEqual(resp.status_code, 404)

    def test_review_gone_after_deletion(self):
        """Après suppression, GET renvoie 404."""
        user_id = self.create_user().get_json()['id']
        place_id = self.create_place(user_id).get_json()['id']
        review_id = self.create_review(user_id, place_id).get_json()['id']
        self.client.delete(f'/api/v1/reviews/{review_id}')
        resp = self.client.get(f'/api/v1/reviews/{review_id}')
        self.assertEqual(resp.status_code, 404)


# ====================================================================== #
#                         INTEGRATION TESTS                                #
# ====================================================================== #

class TestIntegration(BaseTestCase):
    """Tests d'intégration couvrant des scénarios end-to-end."""

    def test_full_workflow(self):
        """
        Scénario complet :
        1. Créer un utilisateur
        2. Créer une amenité
        3. Créer une place avec l'owner + amenité
        4. Créer une review pour cette place
        5. Récupérer les reviews de la place
        6. Supprimer la review
        """
        # 1. Utilisateur
        user = self.create_user(email="full@example.com").get_json()
        self.assertIn('id', user)

        # 2. Amenité
        amenity = self.create_amenity("Gym").get_json()
        self.assertIn('id', amenity)

        # 3. Place
        place = self.create_place(
            user['id'],
            amenity_ids=[amenity['id']],
            title="Full Workflow Place"
        ).get_json()
        self.assertIn('id', place)
        self.assertEqual(len(place['amenities']), 1)

        # 4. Review
        review = self.create_review(user['id'], place['id'], text="Awesome!").get_json()
        self.assertIn('id', review)

        # 5. Reviews par place
        resp = self.client.get(f"/api/v1/places/{place['id']}/reviews")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 1)

        # 6. Suppression
        del_resp = self.client.delete(f"/api/v1/reviews/{review['id']}")
        self.assertEqual(del_resp.status_code, 200)

    def test_multiple_users_same_place(self):
        """Plusieurs utilisateurs peuvent créer des reviews pour la même place."""
        owner_id = self.create_user(email="owner@ex.com").get_json()['id']
        user2_id = self.create_user(
            email="user2@ex.com", first_name="Bob"
        ).get_json()['id']
        place_id = self.create_place(owner_id).get_json()['id']

        self.create_review(owner_id, place_id, text="Own review")
        self.create_review(user2_id, place_id, text="Guest review")

        resp = self.client.get(f'/api/v1/places/{place_id}/reviews')
        self.assertEqual(len(resp.get_json()), 2)

    def test_place_response_structure(self):
        """La réponse d'une place contient bien owner et amenities."""
        owner_id = self.create_user().get_json()['id']
        place = self.create_place(owner_id).get_json()
        self.assertIn('id', place)
        self.assertIn('title', place)
        self.assertIn('price', place)
        self.assertIn('latitude', place)
        self.assertIn('longitude', place)
        self.assertIn('owner', place)
        self.assertIn('amenities', place)

    def test_user_list_grows_with_creations(self):
        """La liste des utilisateurs s'agrandit à chaque création."""
        emails = [f"user{i}@example.com" for i in range(3)]
        for i, email in enumerate(emails):
            self.create_user(email=email, first_name=f"User{i}")

        resp = self.client.get('/api/v1/users/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(resp.get_json()), 3)


if __name__ == '__main__':
    unittest.main(verbosity=2)
