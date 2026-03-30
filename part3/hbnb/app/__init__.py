from flask import Flask
from flask_restx import Api
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy

jwt = JWTManager()
bcrypt = Bcrypt()
db = SQLAlchemy()


def create_app(config_class="config.DevelopmentConfig"):
    app = Flask(__name__)
    CORS(app)
    app.config.from_object(config_class)

    # Initialise Flask-Bcrypt avec l'app et initialise JWT manager mais aussi la database
    bcrypt.init_app(app)
    jwt.init_app(app)
    db.init_app(app)

    # Imports déférés — évite les imports circulaires au niveau module
    from app.api.v1.users import api as users_ns
    from app.api.v1.amenities import api as amenities_ns
    from app.api.v1.places import api as places_ns
    from app.api.v1.reviews import api as reviews_ns
    from app.api.v1.auth import api as auth_ns

    api = Api(
        app, version='1.0',
        title='HBnB API',
        description='HBnB Application API',
        doc='/api/v1/',
        authorizations={
            'BearerAuth': {
                'type': 'apiKey',
                'in': 'header',
                'name': 'Authorization',
                'description': 'JWT — format: Bearer <token>'
            }
        }
    )

    api.add_namespace(users_ns, path='/api/v1/users')
    api.add_namespace(amenities_ns, path='/api/v1/amenities')
    api.add_namespace(places_ns, path='/api/v1/places')
    api.add_namespace(reviews_ns, path='/api/v1/reviews')
    api.add_namespace(auth_ns, path='/api/v1/auth')

    # Crée les tables SQLAlchemy si elles n'existent pas encore
    with app.app_context():
        # Import explicite de tous les modèles avant db.create_all()
        # pour que SQLAlchemy enregistre leurs tables dans les métadonnées
        from app.models import user, place, review, amenity
        db.create_all()

    return app
