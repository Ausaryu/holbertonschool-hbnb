import re
from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('users', description='User operations')

email_validation = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def validate_user_payload(data, require_password=True):
    """Valide les champs obligatoires. Retourne un message d'erreur ou None."""
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


# Modèle d'entrée
user_model = api.model('User', {
    'first_name': fields.String(required=True, description='First name of the user'),
    'last_name': fields.String(required=True, description='Last name of the user'),
    'email': fields.String(required=True, description='Email of the user'),
    'password': fields.String(required=True, description='Password of the user')
})

# Modèle de sortie
user_response_model = api.model('UserResponse', {
    'id': fields.String(description='User ID'),
    'first_name': fields.String(description='First name of the user'),
    'last_name': fields.String(description='Last name of the user'),
    'email': fields.String(description='Email of the user')
})


def user_to_dict(user):
    """Sérialise un User sans exposer le password."""
    return {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'email': user.email
    }


@api.route('/')
class UserList(Resource):
    @api.expect(user_model, validate=True)
    @api.response(201, 'User successfully created', user_response_model)
    @api.response(400, 'Email already registered')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new user"""
        user_data = api.payload

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
        """Retrieve a list of all users — password not included"""
        return [user_to_dict(u) for u in facade.get_all_users()], 200


@api.route('/<user_id>')
class UserResource(Resource):
    @api.response(200, 'User details retrieved successfully', user_response_model)
    @api.response(404, 'User not found')
    def get(self, user_id):
        """Get user details by ID — password not included"""
        user = facade.get_user(user_id)
        if not user:
            return {'error': 'User not found'}, 404
        return user_to_dict(user), 200

    @api.expect(user_model, validate=True)
    @api.response(200, 'User successfully updated', user_response_model)
    @api.response(404, 'User not found')
    @api.response(400, 'Invalid input data')
    def put(self, user_id):
        """Update user information"""
        user_data = api.payload

        error = validate_user_payload(user_data, require_password=False)
        if error:
            return {'error': error}, 400

        try:
            updated_user = facade.update_user(user_id, user_data)
        except ValueError as e:
            return {"error": str(e)}, 400
        if not updated_user:
            return {'error': 'User not found'}, 404

        return user_to_dict(updated_user), 200
