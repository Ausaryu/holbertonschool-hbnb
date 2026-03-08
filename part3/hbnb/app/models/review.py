from app.models.base_model import BaseModel


class Review(BaseModel):
    def __init__(self, text, rating, place, user):
        super().__init__()
        if not text or not str(text).strip():
            raise ValueError("'text' is required and cannot be empty")
        self.validate_rating(rating)
        self.text = text
        self.rating = rating  # Devrait être validé (1-5)
        self.place = place   # Instance de Place
        self.user = user     # Instance de User

    @staticmethod
    def validate_rating(rating):
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            raise ValueError("Rating must be an integer between 1 and 5")

    def update(self, data):
        if 'text' in data:
            if not data['text'] or not str(data['text']).strip():
                raise ValueError("'text' is required and cannot be empty")
        if 'rating' in data:
            self.validate_rating(data['rating'])
        super().update(data)
