from flask_restx import Namespace, Resource, fields
from app.services import facade

api = Namespace('reviews', description='Review operations')

review_model = api.model('Review', {
    'text': fields.String(required=True, description='Text of the review'),
    'rating': fields.Integer(required=True, description='Rating of the place (1-5)'),
    'user_id': fields.String(required=True, description='ID of the user'),
    'place_id': fields.String(required=True, description='ID of the place')
})


def marshal_review(review):
    """Sérialise un objet Review en dict JSON."""
    return {
        "id": review.id,
        "text": review.text,
        "rating": review.rating,
        "user_id": review.user.id,
        "place_id": review.place.id
    }


@api.route('/')
class ReviewList(Resource):
    @api.expect(review_model)
    @api.response(201, 'Review successfully created')
    @api.response(400, 'Invalid input data')
    def post(self):
        """Register a new review"""
        data = api.payload

        if not data:
            return {"error": "Payload is empty"}, 400
        if not data.get('text') or not str(data['text']).strip():
            return {"error": "'text' is required and cannot be empty"}, 400
        if data.get('rating') is None:
            return {"error": "'rating' is required"}, 400

        try:
            new_review = facade.create_review(data)
            return marshal_review(new_review), 201
        except ValueError as e:
            return {"error": str(e)}, 400

    @api.response(200, 'List of reviews retrieved successfully')
    def get(self):
        """Retrieve a list of all reviews"""
        return [marshal_review(r) for r in facade.get_all_reviews()], 200


@api.route('/<review_id>')
class ReviewResource(Resource):
    @api.response(200, 'Review details retrieved successfully')
    @api.response(404, 'Review not found')
    def get(self, review_id):
        """Get review details by ID"""
        review = facade.get_review(review_id)
        if not review:
            api.abort(404, "Review not found")
        return marshal_review(review), 200

    @api.expect(review_model)
    @api.response(200, 'Review updated successfully')
    @api.response(404, 'Review not found')
    @api.response(400, 'Invalid input data')
    def put(self, review_id):
        """Update a review's information"""
        try:
            updated_review = facade.update_review(review_id, api.payload)
        except ValueError as e:
            return {"error": str(e)}, 400
        if not updated_review:
            api.abort(404, "Review not found")
        return marshal_review(updated_review), 200

    @api.response(200, 'Review deleted successfully')
    @api.response(404, 'Review not found')
    def delete(self, review_id):
        """Delete a review"""
        if not facade.get_review(review_id):
            api.abort(404, "Review not found")
        facade.delete_review(review_id)
        return {"message": f"Review {review_id} deleted"}, 200
