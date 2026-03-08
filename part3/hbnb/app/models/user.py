import re
from app.models.base_model import BaseModel

email_validation = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


class User(BaseModel):
    def __init__(self, first_name, last_name, email, password, is_admin=False):
        super().__init__()
        self.first_name = self._validate_non_empty(first_name, 'first_name', max_len=50)
        self.last_name = self._validate_non_empty(last_name, 'last_name', max_len=50)
        self.email = self._validate_email(email)
        self.is_admin = is_admin  # False par défaut
        self.password = self._validate_non_empty(password, 'password')
        self.places = []

    @staticmethod
    def _validate_non_empty(value, field_name, max_len=None):
        if not value or not str(value).strip():
            raise ValueError(f"'{field_name}' is required and cannot be empty")
        if max_len and len(str(value)) > max_len:
            raise ValueError(f"'{field_name}' must not exceed {max_len} characters")
        return value
    
    @staticmethod
    def _validate_email(email):
        if not email or not str(email).strip():
            raise ValueError("'email' is required and cannot be empty")
        if not EMAIL_REGEX.match(email):
            raise ValueError("Invalid email format")
        return email

    def add_place(self, place):
        """Add a place to the user"""
        self.places.append(place)
