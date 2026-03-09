from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager

jwt = JWTManager()

bcrypt = Bcrypt()

from app.api.v1.users import api as users_ns
from app.api.v1.amenities import api as amenities_ns
from app.api.v1.places import api as places_ns
from app.api.v1.reviews import api as reviews_ns
from app.services import facade


def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialise Flask-Bcrypt avec l'app
    bcrypt.init_app(app)

    api = Api(app, version='1.0', title='HBnB API',
              description='HBnB Application API', doc='/api/v1/')

    # Réinitialise les dépôts du facade à chaque création d'app
    # (indispensable pour que chaque test reparte sur des données vierges)
    from app.persistence.repository import InMemoryRepository
    facade.user_repo = InMemoryRepository()
    facade.place_repo = InMemoryRepository()
    facade.review_repo = InMemoryRepository()
    facade.amenity_repo = InMemoryRepository()

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    return app
