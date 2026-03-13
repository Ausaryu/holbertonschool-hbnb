from app.persistence.repository import SQLAlchemyRepository, InMemoryRepository
from app.models.user import User
from app.models.amenity import Amenity
from app.models.place import Place
from app.models.review import Review
from app.persistence.repository import UserRepository


class HBnBFacade:
    def __init__(self):
        self._user_repo_instance = None
        self._amenity_repo_instance = None
        self._place_repo_instance = None
        self._review_repo_instance = None

    # ------------------------------------------------------------------ #
    #  Lazy repo properties
    # ------------------------------------------------------------------ #

    @property
    def user_repo(self):
        if self._user_repo_instance is None:
            self._user_repo_instance = UserRepository()
        return self._user_repo_instance

    @user_repo.setter
    def user_repo(self, value):
        self._user_repo_instance = value

    @property
    def amenity_repo(self):
        if self._amenity_repo_instance is None:
            from app.models.amenity import Amenity
            self._amenity_repo_instance = SQLAlchemyRepository(Amenity)
        return self._amenity_repo_instance

    @amenity_repo.setter
    def amenity_repo(self, value):
        self._amenity_repo_instance = value

    @property
    def place_repo(self):
        if self._place_repo_instance is None:
            from app.models.place import Place
            self._place_repo_instance = SQLAlchemyRepository(Place)
        return self._place_repo_instance

    @place_repo.setter
    def place_repo(self, value):
        self._place_repo_instance = value

    @property
    def review_repo(self):
        if self._review_repo_instance is None:
            from app.models.review import Review
            self._review_repo_instance = SQLAlchemyRepository(Review)
        return self._review_repo_instance

    @review_repo.setter
    def review_repo(self, value):
        self._review_repo_instance = value

    # ------------------------------------------------------------------ #
    #  Users
    # ------------------------------------------------------------------ #

    def create_user(self, user_data):
        """Crée un utilisateur — le password est hashé dans le modèle User."""
        user = User(**user_data)
        self.user_repo.add(user)
        return user

    def get_user(self, user_id):
        return self.user_repo.get(user_id)

    def get_user_by_email(self, email):
        return self.user_repo.get_by_attribute('email', email)

    def get_all_users(self):
        return self.user_repo.get_all()

    def update_user(self, user_id, user_data):
        user = self.user_repo.get(user_id)
        if not user:
            return None

        if "email" in user_data and user_data["email"] != user.email:
            if self.get_user_by_email(user_data["email"]):
                raise ValueError("Email already registered")

        # Si un nouveau password est fourni, le hacher via la méthode du modèle
        if "password" in user_data:
            user.hash_password(user_data.pop("password"))

        self.user_repo.update(user_id, user_data)
        return self.user_repo.get(user_id)

    # ------------------------------------------------------------------ #
    #  Amenities
    # ------------------------------------------------------------------ #

    def create_amenity(self, amenity_data):
        amenity = Amenity(**amenity_data)
        self.amenity_repo.add(amenity)
        return amenity

    def get_amenity(self, amenity_id):
        return self.amenity_repo.get(amenity_id)

    def get_amenity_by_name(self, name):
        return self.amenity_repo.get_by_attribute('name', name)

    def get_all_amenities(self):
        return self.amenity_repo.get_all()

    def update_amenity(self, amenity_id, amenity_data):
        amenity = self.amenity_repo.get(amenity_id)
        if not amenity:
            return None
        self.amenity_repo.update(amenity_id, amenity_data)
        return self.amenity_repo.get(amenity_id)

    # ------------------------------------------------------------------ #
    #  Places
    # ------------------------------------------------------------------ #

    def create_place(self, place_data):
        owner = self.user_repo.get(place_data['owner_id'])
        if not owner:
            raise ValueError("Owner not found")

        if not place_data.get('title'):
            raise ValueError("Title is required")

        amenity_ids = place_data.pop('amenities', [])

        new_place = Place(
            title=place_data['title'],
            description=place_data.get('description', ""),
            price=place_data['price'],
            latitude=place_data['latitude'],
            longitude=place_data['longitude'],
            owner=owner
        )

        for amenity_id in amenity_ids:
            amenity = self.amenity_repo.get(amenity_id)
            if amenity:
                new_place.add_amenity(amenity)

        self.place_repo.add(new_place)
        return new_place

    def get_place(self, place_id):
        return self.place_repo.get(place_id)

    def get_all_places(self):
        return self.place_repo.get_all()

    def update_place(self, place_id, place_data):
        place = self.place_repo.get(place_id)
        if not place:
            return None
        place.update(place_data)
        return self.place_repo.get(place_id)

    def delete_place(self, place_id):
        return self.place_repo.delete(place_id)

    # ------------------------------------------------------------------ #
    #  Reviews
    # ------------------------------------------------------------------ #

    def create_review(self, review_data):
        user = self.get_user(review_data['user_id'])
        place = self.get_place(review_data['place_id'])

        if not user:
            raise ValueError("User not found")
        if not place:
            raise ValueError("Place not found")

        new_review = Review(
            text=review_data['text'],
            rating=review_data['rating'],
            place=place,
            user=user
        )
        place.reviews.append(new_review)
        self.review_repo.add(new_review)
        return new_review

    def get_review(self, review_id):
        return self.review_repo.get(review_id)

    def get_all_reviews(self):
        return self.review_repo.get_all()

    def get_reviews_by_place(self, place_id):
        return [r for r in self.get_all_reviews() if r.place.id == place_id]

    def get_review_by_user_and_place(self, user_id, place_id):
        """Retourne la review d'un user pour une place donnée, ou None."""
        for r in self.get_all_reviews():
            if r.user.id == user_id and r.place.id == place_id:
                return r
        return None

    def update_review(self, review_id, review_data):
        review = self.review_repo.get(review_id)
        if not review:
            return None
        review.update(review_data)
        return self.review_repo.get(review_id)

    def delete_review(self, review_id):
        return self.review_repo.delete(review_id)
