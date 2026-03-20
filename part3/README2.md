# HBnB — Part 3 : Authentication, Authorization & Database Persistence

## Overview

Part 3 extends the HBnB REST API with:

- **JWT authentication** via Flask-JWT-Extended
- **Role-based access control** (regular user vs admin)
- **Database persistence** via SQLAlchemy (SQLite in development)
- **bcrypt password hashing**
- **SQL schema scripts** for independent database provisioning
- **ER diagram documentation** for the relational schema

---

## Project Structure

```bash
part3/hbnb/
├── app/
│   ├── __init__.py               # App factory — bcrypt, JWT, SQLAlchemy init
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py           # POST /api/v1/auth/login
│   │       ├── users.py          # CRUD /api/v1/users/
│   │       ├── places.py         # CRUD /api/v1/places/
│   │       ├── reviews.py        # CRUD /api/v1/reviews/
│   │       └── amenities.py      # CRUD /api/v1/amenities/
│   ├── models/
│   │   ├── base_model.py         # Abstract base — id, created_at, updated_at
│   │   ├── user.py               # User entity + bcrypt
│   │   ├── place.py              # Place entity + place_amenity association table
│   │   ├── review.py             # Review entity (CHECK + UNIQUE constraints)
│   │   └── amenity.py            # Amenity entity
│   ├── persistence/
│   │   └── repository.py         # SQLAlchemyRepository, UserRepository
│   └── services/
│       ├── __init__.py           # Facade singleton
│       └── facade.py             # HBnBFacade — all business logic
├── Scripts/
│   ├── schema.sql                # Full schema (compatible MySQL & SQLite)
│   ├── initial_data.sql          # Admin user + 3 amenities
│   └── test_crud.sql             # CRUD test queries
├── Test/
│   └── test_hbnb_api.py          # Unittest suite (in-memory SQLite)
├── ER_diagram.pdf.pdf            # Entity-Relationship diagram of the database schema
├── ER_diagram.png                # Preview image displayed directly in the README
├── config.py                     # DevelopmentConfig, TestingConfig
├── run.py                        # App entrypoint + admin seed
└── requirements.txt
```

---

## Requirements

```bash
flask
flask-restx
flask-bcrypt
flask-jwt-extended
sqlalchemy
flask-sqlalchemy
```

Install:

```bash
pip install -r requirements.txt
```

---

## Running the Application

```bash
cd part3/hbnb
python3 run.py
```

The app starts on `http://127.0.0.1:5000`.

Swagger UI: `http://127.0.0.1:5000/api/v1/`

On first run, `run.py` seeds a default admin account:

| Field    | Value           |
|----------|-----------------|
| email    | admin@hbnb.io   |
| password | admin123        |
| is_admin | true            |

> **Note:** if you modify models after the DB was created, delete `instance/development.db` and restart to rebuild the schema.

---

## Authentication

### Login

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "admin@hbnb.io",
  "password": "admin123"
}
```

Response:

```json
{
  "access_token": "<JWT>"
}
```

Use the token on protected endpoints:

```http
Authorization: Bearer <JWT>
```

---

## API Endpoints

### Auth

| Method | Endpoint              | Auth     | Description        |
|--------|-----------------------|----------|--------------------|
| POST   | `/api/v1/auth/login`  | Public   | Get a JWT token    |

### Users

| Method | Endpoint                | Auth          | Description                        |
|--------|-------------------------|---------------|------------------------------------|
| GET    | `/api/v1/users/`        | Public        | List all users                     |
| POST   | `/api/v1/users/`        | Admin only    | Create a new user                  |
| GET    | `/api/v1/users/<id>`    | Public        | Get user by ID                     |
| PUT    | `/api/v1/users/<id>`    | JWT required  | Update user (self or admin)        |

POST requires a valid admin JWT. Regular users can only update `first_name` and `last_name`.

Admins can also update `email` and `password`.

### Amenities

| Method | Endpoint                    | Auth         | Description             |
|--------|-----------------------------|--------------|-------------------------|
| GET    | `/api/v1/amenities/`        | Public       | List all amenities      |
| POST   | `/api/v1/amenities/`        | Admin only   | Create an amenity       |
| GET    | `/api/v1/amenities/<id>`    | Public       | Get amenity by ID       |
| PUT    | `/api/v1/amenities/<id>`    | Admin only   | Update an amenity       |

### Places

| Method | Endpoint                        | Auth              | Description                       |
|--------|---------------------------------|-------------------|-----------------------------------|
| GET    | `/api/v1/places/`               | Public            | List all places                   |
| POST   | `/api/v1/places/`               | JWT required      | Create a place (owner = you)      |
| GET    | `/api/v1/places/<id>`           | Public            | Get place by ID                   |
| PUT    | `/api/v1/places/<id>`           | Owner or admin    | Update place details              |
| DELETE | `/api/v1/places/<id>`           | Owner or admin    | Delete a place                    |
| GET    | `/api/v1/places/<id>/reviews`   | Public            | List reviews for a place          |

PUT only allows: `title`, `description`, `price`, `latitude`, `longitude`.

`owner_id` and `amenities` cannot be changed via PUT.

### Reviews

| Method | Endpoint                | Auth              | Description                     |
|--------|-------------------------|-------------------|---------------------------------|
| GET    | `/api/v1/reviews/`      | Public            | List all reviews                |
| POST   | `/api/v1/reviews/`      | JWT required      | Create a review                 |
| GET    | `/api/v1/reviews/<id>`  | Public            | Get review by ID                |
| PUT    | `/api/v1/reviews/<id>`  | Author or admin   | Update review text/rating       |
| DELETE | `/api/v1/reviews/<id>`  | Author or admin   | Delete a review                 |

Business rules enforced on POST:
- Cannot review your own place → `400`
- Cannot review the same place twice → `400`

PUT only allows: `text`, `rating`. `user_id` and `place_id` are immutable.

---

## Database

### ORM (SQLAlchemy)

Tables created automatically on startup via `db.create_all()`:

| Table           | Description                        |
|-----------------|------------------------------------|
| `users`         | User accounts                      |
| `places`        | Listings                           |
| `reviews`       | Reviews with CHECK + UNIQUE        |
| `amenities`     | Amenity catalogue                  |
| `place_amenity` | Many-to-many Place ↔ Amenity       |

### ER Diagram

The relational schema is also documented in [ER_diagram.pdf.pdf](./ER_diagram.pdf.pdf), which provides a visual overview of the database entities and their relationships.

![ER Diagram](./ER_diagram.png)


### SQL Scripts (independent of ORM)

Located in `Scripts/`:

```bash
# SQLite
sqlite3 instance/development.db < Scripts/Schema.sql
sqlite3 instance/development.db < Scripts/Initial_data.sql
sqlite3 instance/development.db < Scripts/Test_crud.sql

# MySQL
mysql -u root -p hbnb < Scripts/Schema.sql
mysql -u root -p hbnb < Scripts/Initial_data.sql
```

---

## Running the Tests

Tests use an **in-memory SQLite database** — each test starts with a clean DB.

```bash
cd part3/hbnb
python3 -m pytest Test/test_hbnb_api.py -v
# or
python3 -m unittest Test/test_hbnb_api -v
```

The test suite covers: user CRUD, amenity CRUD, place CRUD, review CRUD,
JWT auth, duplicate detection, and access control (403/401 cases).

---

## Configuration

| Config class        | DB URI                      | Used for            |
|---------------------|-----------------------------|---------------------|
| `DevelopmentConfig` | `sqlite:///development.db`  | `python3 run.py`    |
| `TestingConfig`     | `sqlite:///:memory:`        | Test suite          |

Set via `create_app("config.DevelopmentConfig")` or `create_app("config.TestingConfig")`.

## Authors

- **Antoine Gousset** — [GitHub](https://github.com/Antgst)
- **Gwendal Boisard** — [GitHub](https://github.com/Gwendal-B)
- **Yonas Houriez** — [GitHub](https://github.com/Ausaryu)

See `AUTHORS`.
