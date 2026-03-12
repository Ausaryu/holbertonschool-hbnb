from app.models.base_model import BaseModel
from app import db

class Amenity(BaseModel):
    __tablename__ = 'amenities'

    name = db.Column(db.String(50), nullable=False, unique=True)

    def __init__(self, name):
        super().__init__()
        if not name or not str(name).strip():
            raise ValueError("'name' is required and cannot be empty")
        if len(str(name)) > 50:
            raise ValueError("'name' must not exceed 50 characters")
        self.name = name
