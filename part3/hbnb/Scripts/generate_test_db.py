#!/usr/bin/env python3
"""Recreate part3/hbnb/instance/development.db with rich test data.

This version only relies on the Python standard library + htpasswd
(which is available on most Unix systems), so it does not need Flask
or project dependencies to be installed.
"""

from __future__ import annotations

import sqlite3
import bcrypt
import uuid
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "development.db"
SCHEMA_PATH = BASE_DIR / "Scripts" / "Schema.sql"


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def new_id() -> str:
    return str(uuid.uuid4())

def bcrypt_hash(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


USER_SEED = [
    ("Admin", "HBnB", "admin@hbnb.io", "admin1234", True),
    ("Super", "Manager", "manager@hbnb.io", "manager1234", True),
    ("Alice", "Martin", "alice@example.com", "alice1234", False),
    ("Bob", "Durand", "bob@example.com", "bob1234", False),
    ("Chloe", "Bernard", "chloe@example.com", "chloe1234", False),
    ("David", "Petit", "david@example.com", "david1234", False),
    ("Emma", "Robert", "emma@example.com", "emma1234", False),
    ("Farid", "Leroy", "farid@example.com", "farid1234", False),
]

AMENITY_NAMES = [
    "WiFi",
    "Swimming Pool",
    "Air Conditioning",
    "Kitchen",
    "Free Parking",
    "TV",
    "Washing Machine",
    "Balcony",
    "Pet Friendly",
    "Breakfast",
]

PLACE_SEED = [
    ("Loft Rennes Centre", "Grand loft moderne proche du centre-ville.", 95.0, 48.1113, -1.6800, "alice@example.com", ["WiFi", "Kitchen", "TV", "Washing Machine"]),
    ("Maison avec jardin", "Maison familiale calme avec jardin et parking.", 140.0, 48.1170, -1.7002, "bob@example.com", ["WiFi", "Free Parking", "Kitchen", "Pet Friendly"]),
    ("Studio cosy gare", "Petit studio idéal pour un court séjour.", 58.0, 48.1039, -1.6725, "chloe@example.com", ["WiFi", "TV", "Air Conditioning"]),
    ("Villa piscine Bretagne", "Grande villa avec piscine pour les vacances.", 240.0, 48.3904, -4.4861, "david@example.com", ["WiFi", "Swimming Pool", "Free Parking", "Balcony", "Kitchen"]),
    ("Appartement vue mer", "Appartement lumineux avec vue sur la mer.", 180.0, 48.6484, -2.0257, "emma@example.com", ["WiFi", "Balcony", "TV", "Breakfast"]),
    ("Cabane nature", "Séjour au calme au milieu des arbres.", 110.0, 47.9956, -4.1020, "farid@example.com", ["Kitchen", "Free Parking", "Pet Friendly"]),
    ("Penthouse admin demo", "Place créée par un compte admin pour les tests.", 320.0, 48.8566, 2.3522, "admin@hbnb.io", ["WiFi", "Air Conditioning", "Balcony", "TV"]),
    ("Appartement manager demo", "Annonce secondaire pour vérifier plusieurs profils admin.", 125.0, 43.2965, 5.3698, "manager@hbnb.io", ["WiFi", "Kitchen", "Breakfast"]),
]

REVIEW_SEED = [
    ("Super séjour, appartement très propre.", 5, "Loft Rennes Centre", "bob@example.com"),
    ("Très bien placé et calme la nuit.", 4, "Loft Rennes Centre", "chloe@example.com"),
    ("Jardin agréable, parfait pour une famille.", 5, "Maison avec jardin", "alice@example.com"),
    ("Bon logement mais un peu loin du centre.", 4, "Maison avec jardin", "emma@example.com"),
    ("Studio pratique pour 2 jours.", 4, "Studio cosy gare", "david@example.com"),
    ("Piscine top, maison immense.", 5, "Villa piscine Bretagne", "farid@example.com"),
    ("Vue magnifique, je reviendrai.", 5, "Appartement vue mer", "alice@example.com"),
    ("Cabane originale et reposante.", 4, "Cabane nature", "bob@example.com"),
    ("Place premium utile pour tester le front admin.", 5, "Penthouse admin demo", "emma@example.com"),
    ("Annonce propre, petit déjeuner apprécié.", 4, "Appartement manager demo", "chloe@example.com"),
]


def main() -> None:
    INSTANCE_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
    cur = conn.cursor()

    ts = now()

    users_by_email: dict[str, str] = {}
    for first_name, last_name, email, password, is_admin in USER_SEED:
        user_id = new_id()
        users_by_email[email] = user_id
        cur.execute(
            """
            INSERT INTO users (id, first_name, last_name, email, password, is_admin, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, first_name, last_name, email, bcrypt_hash(password), int(is_admin), ts, ts),
        )

    amenities_by_name: dict[str, str] = {}
    for name in AMENITY_NAMES:
        amenity_id = new_id()
        amenities_by_name[name] = amenity_id
        cur.execute(
            "INSERT INTO amenities (id, name, created_at, updated_at) VALUES (?, ?, ?, ?)",
            (amenity_id, name, ts, ts),
        )

    places_by_title: dict[str, str] = {}
    for title, description, price, latitude, longitude, owner_email, amenity_names in PLACE_SEED:
        place_id = new_id()
        places_by_title[title] = place_id
        cur.execute(
            """
            INSERT INTO places (id, title, description, price, latitude, longitude, owner_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (place_id, title, description, price, latitude, longitude, users_by_email[owner_email], ts, ts),
        )
        for amenity_name in amenity_names:
            cur.execute(
                "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?, ?)",
                (place_id, amenities_by_name[amenity_name]),
            )

    for text, rating, place_title, reviewer_email in REVIEW_SEED:
        cur.execute(
            """
            INSERT INTO reviews (id, text, rating, user_id, place_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (new_id(), text, rating, users_by_email[reviewer_email], places_by_title[place_title], ts, ts),
        )

    conn.commit()

    counts = {
        "users": cur.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "admins": cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0],
        "amenities": cur.execute("SELECT COUNT(*) FROM amenities").fetchone()[0],
        "places": cur.execute("SELECT COUNT(*) FROM places").fetchone()[0],
        "reviews": cur.execute("SELECT COUNT(*) FROM reviews").fetchone()[0],
        "place_amenity": cur.execute("SELECT COUNT(*) FROM place_amenity").fetchone()[0],
    }
    conn.close()

    print(f"DB generated: {DB_PATH}")
    print(counts)
    print("Accounts:")
    for _, _, email, password, is_admin in USER_SEED:
        print(f"- {email} / {password} / {'admin' if is_admin else 'user'}")


if __name__ == "__main__":
    main()
