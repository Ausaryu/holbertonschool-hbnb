import re
from flask_restx import Namespace, Resource, fields
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.services import facade

api = Namespace('users', description='User operations')

email_validation = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validate_user_payload(data, require_password=True):
    """Valide les champs obligatoires pour la création. Retourne un message d'erreur ou None."""
    if not data:
        return "Payload is empty"
    for field in ('first_name', 'last_name', 'email'):
        value = data.get(field)
        if not value or not str(value).strip():
            return f"'{field}' is required and cannot be empty"
    if require_password:
        password = data.get('password')
        if not password or not str(password).strip():
            return "'password' is required and cannot be empty"
    if not email_validation.match(data['email']):
        return "Invalid email format"
    return None


def validate_user_update_payload(data):
    """Valide le payload de mise à jour (first_name, last_name uniquement)."""
    if not data:
        return "Payload is empty"
    # email et password ne peuvent pas être modifiés via ce endpoint
    if 'email' in data:
        return "You cannot modify your email"
    if 'password' in data:
        return "You cannot modify your password"
    for field in ('first_name', 'last_name'):
        value = data.get(field)
        if value is not None and not str(value).strip():
            return f"'{field}' cannot be empty"
    return None


def validate_admin_update_payload(data):
    """Valide le payload de mise à jour (first_name, last_name)."""
    if not data:
        return "Payload is empty"
    if 'email' in data:
        email = data["email"]
        if not email_validation.match(data['email']):
            return "Invalid email format"
        if not str(email).strip():
            return "'email' cannot be empty"
    if 'password' in data:
        password = data["password"]
        if not str(password).strip():
            return "'password' cannot be empty"
    for field in ('first_name', 'last_name'):
        value = data.get(field)
        if value is not None and not str(value).strip():
            return f"'{field}' cannot be empty"
    return None


# Modèle d'entrée pour la création (inclut email + password)
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name':  fields.String(required=True, description='Last name of the user'),
    'email':      fields.String(required=True, description='Email of the user'),
    'password':   fields.String(required=True, description='Password of the user'),
    'is_admin':   fields.Boolean(required=True, description='Status admin of the user'),
})

# Modèle d'entrée pour la mise à jour (first_name et last_name seulement)
user_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name':  fields.String(description='Last name of the user')
})

# Modèle d'entrée pour la mise à jour admin
admin_update_model = api.model('UserUpdate', {
    'first_name': fields.String(description='First name of the user'),
    'last_name':  fields.String(description='Last name of the user'),
    'email':      fields.String(description='Email of the user'),
    'password':   fields.String(description='Password of the user')
})

# Modèle de sortie (sans password)
user_response_model = api.model('UserResponse', {
    'id':         fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the user'),
    'last_name':  fields.String(description='Last name of the user'),
    'email':      fields.String(description='Email of the user')
})


def user_to_dict(user):
    """Sérialise un User SANS exposer le password."""
    return {
        'id':         user.id,
        'first_name': user.first_name,
        'last_name':  user.last_name,
        'email':      user.email
    }


@api.route('/')
class UserList(Resource):
    @jwt_required()
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created', user_response_model)
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user (public endpoint)"""
        user_data = api.payload
        claims = get_jwt()

        if not claims.get('is_admin'):
            return {'error': 'Admin privileges required'}, 403

        error = validate_user_payload(user_data, require_password=True)
        if error:
            return {'error': error}, 400

        if facade.get_user_by_email(user_data['email']):
            return {'error': 'Email already registered'}, 400

        try:
            new_user = facade.create_user(user_data)
        except ValueError as e:
            return {'error': str(e)}, 400

        return user_to_dict(new_user), 201

    @api.response(200, 'List of users retrieved successfully')
    def get(self):
        """Retrieve a list of all users (public endpoint)"""
        return [user_to_dict(u) for u in facade.get_all_users()], 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully', user_response_model)
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID (public endpoint)"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user_to_dict(user), 200

    @jwt_required()
    @api.doc(security='BearerAuth')
    @api.expect(user_update_model, validate=True)
    @api.response(200, 'User successfully updated', user_response_model)
    @api.response(400, 'Invalid input data — email and password cannot be modified')
    @api.response(401, 'Authentication required')
    @api.response(403, 'Unauthorized action')
    @api.response(404, 'User not found')
    def put(self, user_id):
        """Update user first/last name — email and password cannot be changed here"""
        current_user_id = get_jwt_identity()
        claims = get_jwt()
        
        is_admin = claims.get('is_admin', False)
        # Seul l'utilisateur lui-même ou un admin peut modifier
        if current_user_id != user_id and not is_admin:
            return {'error': 'Unauthorized action'}, 403

        user_data = api.payload

        if is_admin:
            error = validate_admin_update_payload(user_data)
        else:
            error = validate_user_update_payload(user_data)

        if error:
            return {'error': error}, 400

        try:
            updated_user = facade.update_user(user_id, user_data)
        except ValueError as e:
            return {"error": str(e)}, 400
        if not updated_user:
            return {'error': 'User not found'}, 404

        return user_to_dict(updated_user), 200
