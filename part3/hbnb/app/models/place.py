from app.models.base_model import BaseModel


class Place(BaseModel):
    def __init__(self, title, description, price, latitude, longitude, owner):
        self._validate_title(title)
        self.validate_place_data(price, latitude, longitude)
        super().__init__()
        self.title = title
        self.description = description
        self.price = price
        self.latitude = latitude
        self.longitude = longitude
        self.owner = owner  # Instance de User
        self.amenities = []  # Liste d'instances d'Amenity
        self.reviews = []   # Liste d'instances de Review

    @staticmethod
    def _validate_title(title):
        if not title or not str(title).strip():
            raise ValueError("'title' is required and cannot be empty")
        if len(str(title)) > 100:
            raise ValueError("'title' must not exceed 100 characters")

    @staticmethod
    def validate_place_data(price, latitude, longitude):
        """
        Méthode de validation pour garantir l'intégrité des données métier
        """
        if price <= 0:
            raise ValueError("Price must be a positive value.")
        if not (-90.0 <= latitude <= 90.0):
            raise ValueError("Latitude must be between -90.0 and 90.0.")
        if not (-180.0 <= longitude <= 180.0):
            raise ValueError("Longitude must be between -180.0 and 180.0.")

    def update(self, data):
        """
        Surcharge de la méthode update pour inclure la
        validation lors de la modif
        """
        # Vérifier si les données sensibles sont présentes pour les valider
        new_title = data.get('title', self.title)
        new_price = data.get('price', self.price)
        new_lat = data.get('latitude', self.latitude)
        new_long = data.get('longitude', self.longitude)

        self._validate_title(new_title)
        self.validate_place_data(new_price, new_lat, new_long)

        # Appel de la méthode parente pour mettre à jour les autres champs
        super().update(data)

    def add_amenity(self, amenity):
        if amenity not in self.amenities:
            self.amenities.append(amenity)

    def add_review(self, review):
        if review not in self.reviews:
            self.reviews.append(review)
