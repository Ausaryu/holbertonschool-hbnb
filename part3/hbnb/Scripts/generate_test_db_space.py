#!/usr/bin/env python3
"""Recreate part3/hbnb/instance/development.db with themed space/lunar test data.

- Uses only SQLite + bcrypt Python package
- Replaces instance/development.db
- Keeps the original demo users and adds a few themed accounts
- Generates 10 places, amenities, many-to-many links, and very varied reviews
"""

from __future__ import annotations

import sqlite3
import uuid
from datetime import datetime
from pathlib import Path

import bcrypt

BASE_DIR = Path(__file__).resolve().parent.parent
INSTANCE_DIR = BASE_DIR / "instance"
DB_PATH = INSTANCE_DIR / "development.db"
SCHEMA_PATH = BASE_DIR / "Scripts" / "Schema.sql"


def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def new_id() -> str:
    return str(uuid.uuid4())


def bcrypt_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


USER_SEED = [
    ("Admin", "HBnB", "admin@hbnb.io", "admin1234", True),
    ("Super", "Manager", "manager@hbnb.io", "manager1234", True),
    ("Alice", "Martin", "alice@example.com", "alice1234", False),
    ("Bob", "Durand", "bob@example.com", "bob1234", False),
    ("Chloe", "Bernard", "chloe@example.com", "chloe1234", False),
    ("David", "Petit", "david@example.com", "david1234", False),
    ("Emma", "Robert", "emma@example.com", "emma1234", False),
    ("Farid", "Leroy", "farid@example.com", "farid1234", False),
    ("Selene", "Vargas", "selene@example.com", "selene1234", False),
    ("Neil", "Kessler", "neil@example.com", "neil1234", False),
    ("Luna", "Moreau", "luna@example.com", "luna1234", False),
    ("Orion", "Vale", "orion@example.com", "orion1234", False),
    ("Ender", "Man", "enderman@void.net", "ender1234", False),
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
    "Moon Viewport",
    "Oxygen Garden",
    "Meteor Shield",
    "Low Gravity Gym",
    "Docking Bay",
    "Holographic Cinema",
    "Stargazing Dome",
    "Rover Garage",
    "Cryo Suite",
    "Redstone Workshop",
]

PLACE_SEED = [
    {
        "id": "c684cf7a-e33a-4696-a4ae-a21df5c62059",
        "title": "Retraite Mer de la Tranquillité",
        "description": "Une vaste résidence lunaire installée près de la Mer de la Tranquillité, pensée pour les voyageurs qui veulent alterner silence cosmique, panorama sur la Terre et confort haut de gamme.",
        "price": 128.0,
        "latitude": 22.3,
        "longitude": 31.2,
        "owner_email": "alice@example.com",
        "amenities": ["WiFi", "Kitchen", "TV", "Moon Viewport", "Stargazing Dome", "Breakfast"],
    },
    {
        "id": "8e119b31-da24-4a99-bc4c-2c63c04eb502",
        "title": "Habitat Jardin Lunaire",
        "description": "Un habitat familial sous dômes renforcés sur la Lune, avec serre intérieure, coin repas lumineux et espaces pensés pour les séjours longs loin de l'agitation terrestre.",
        "price": 72.0,
        "latitude": 18.7,
        "longitude": 14.8,
        "owner_email": "bob@example.com",
        "amenities": ["WiFi", "Kitchen", "Oxygen Garden", "Free Parking", "Rover Garage"],
    },
    {
        "id": "7c959365-dbeb-4bd6-8528-72846a030845",
        "title": "Studio Cratère Écho",
        "description": "Un studio compact sur la Lune, protégé sous une couche régolithique, idéal pour une escale courte avec vue sur un cratère paisible et des couchers de Terre spectaculaires.",
        "price": 34.0,
        "latitude": -12.4,
        "longitude": 44.6,
        "owner_email": "chloe@example.com",
        "amenities": ["WiFi", "Air Conditioning", "TV", "Moon Viewport"],
    },
    {
        "id": "6cb22992-f86c-4d53-b3e5-8ad798e2cb2f",
        "title": "Station spatiale plutonienne",
        "description": "Une station orbitale isolée aux abords de Pluton, avec passerelles panoramiques, modules pressurisés et ambiance de bout du monde pour aventuriers interstellaires.",
        "price": 480.0,
        "latitude": 67.9,
        "longitude": -103.4,
        "owner_email": "david@example.com",
        "amenities": ["WiFi", "Docking Bay", "Holographic Cinema", "Cryo Suite", "Meteor Shield", "Kitchen"],
    },
    {
        "id": "7f36559f-43a3-4ccf-ba07-171a3a9bb6f5",
        "title": "Loft Lever de Terre",
        "description": "Un loft lunaire lumineux tourné vers l'horizon noir, réputé pour son immense baie vitrée qui offre chaque cycle un lever de Terre saisissant.",
        "price": 96.0,
        "latitude": 9.8,
        "longitude": -21.5,
        "owner_email": "emma@example.com",
        "amenities": ["WiFi", "Balcony", "Moon Viewport", "TV", "Washing Machine"],
    },
    {
        "id": "5303dba7-39bb-41be-a2fb-9f9d9b356632",
        "title": "Cité du Néant",
        "description": "Perchée au cœur de l’End, cette End City offre un refuge rare pour les voyageurs en quête de calme absolu. Entre ses passerelles suspendues au-dessus du vide, ses grandes salles en purpur et ses ouvertures sur l’infini, le lieu invite au repos, à la contemplation et aux séjours loin de l’agitation de l’Overworld. Votre hôte, un Enderman discret et soigneux, veille à ce que chaque visiteur profite d’un séjour paisible dans une demeure aussi singulière qu’élégante.",
        "price": 165.0,
        "latitude": -33.3,
        "longitude": 88.8,
        "owner_email": "enderman@void.net",
        "amenities": ["WiFi", "Meteor Shield", "Moon Viewport", "Redstone Workshop", "Stargazing Dome"],
    },
    {
        "id": "106e7dd4-1ac7-41cf-9407-38e64e70bcbc",
        "title": "Base lunaire Zénith",
        "description": "Un penthouse lunaire haut de gamme creusé dans le relief, mêlant matériaux techniques, salon panoramique et équipements premium pour séjours VIP.",
        "price": 320.0,
        "latitude": 41.2,
        "longitude": -12.1,
        "owner_email": "admin@hbnb.io",
        "amenities": ["WiFi", "Air Conditioning", "Balcony", "Low Gravity Gym", "Breakfast", "Holographic Cinema"],
    },
    {
        "id": "8e54156e-efd1-4c1f-b60f-1aa3c9444611",
        "title": "Astéroïde Gamma A45",
        "description": "Un séjour expérimental creusé dans un astéroïde capturé, minimaliste mais fascinant, parfait pour celles et ceux qui veulent vivre une vraie parenthèse spatiale.",
        "price": 210.0,
        "latitude": -5.2,
        "longitude": 133.7,
        "owner_email": "farid@example.com",
        "amenities": ["WiFi", "Docking Bay", "Cryo Suite", "Meteor Shield"],
    },
    {
        "id": "d509a5ff-408e-445d-8c38-40ec124d6638",
        "title": "Refuge Face Cachée",
        "description": "Un refuge discret installé sur la face cachée de la Lune, apprécié pour son calme absolu, ses modules acoustiques et son ciel constellé sans pollution visuelle.",
        "price": 42.0,
        "latitude": -26.1,
        "longitude": -74.4,
        "owner_email": "manager@hbnb.io",
        "amenities": ["WiFi", "Kitchen", "Stargazing Dome", "Breakfast"],
    },
    {
        "id": "877cb025-1a8b-4a2a-82d6-bc5c310814dd",
        "title": "Capsule Horizon 9",
        "description": "Une micro-capsule lunaire pensée pour les voyageurs au budget serré, compacte mais bien optimisée, avec l'essentiel pour dormir au bord du vide.",
        "price": 8.0,
        "latitude": 3.4,
        "longitude": 11.1,
        "owner_email": "selene@example.com",
        "amenities": ["WiFi", "Air Conditioning"],
    },
]

REVIEW_MAP = {
    "Retraite Mer de la Tranquillité": [
        ("bob@example.com", 5, "Vue incroyable sur la Terre. Le logement respire le calme et tout était impeccable."),
        ("chloe@example.com", 4, "Très belle annonce, super bien équipée. J'aurais juste aimé un peu plus d'espace dans le sas d'entrée."),
        ("david@example.com", 5, "Parfait pour déconnecter. Le dôme d'observation la nuit est exceptionnel."),
        ("emma@example.com", 5, "Probablement l'un des plus beaux séjours de mon front de test, très photogénique."),
        ("farid@example.com", 4, "Confort haut niveau et petit déjeuner solide. Prix cohérent pour ce standing."),
        ("selene@example.com", 5, "Ambiance lunaire premium, rien à redire."),
        ("neil@example.com", 4, "Excellente base pour quelques nuits. Check-in fluide."),
        ("luna@example.com", 5, "Le lever de Terre depuis le salon vaut vraiment le détour."),
    ],
    "Habitat Jardin Lunaire": [
        ("alice@example.com", 5, "La serre intérieure est géniale. On sent un vrai effort pour rendre l'habitat vivant."),
        ("chloe@example.com", 4, "Très bon séjour, logement chaleureux malgré le cadre lunaire."),
        ("emma@example.com", 4, "Parfait pour plusieurs jours. Le rover garage est un vrai plus."),
        ("farid@example.com", 5, "Très familial, très propre, et l'espace repas est super agréable."),
        ("selene@example.com", 3, "Sympa dans l'ensemble, mais la déco est un peu sobre à mon goût."),
        ("orion@example.com", 4, "Bonne surprise, surtout pour ce prix."),
    ],
    "Studio Cratère Écho": [
        ("alice@example.com", 4, "Petit mais malin. Nickel pour un court passage."),
        ("bob@example.com", 3, "Le studio fait le job, sans plus. Très bonne vue par contre."),
    ],
    "Station spatiale plutonienne": [
        ("admin@hbnb.io", 5, "Expérience folle. L'isolement et les passerelles donnent une vraie sensation d'expédition."),
        ("alice@example.com", 5, "Clairement une annonce vitrine. Le module cinéma holographique est dingue."),
        ("bob@example.com", 4, "Très impressionnant mais réservé aux amateurs de grand vide spatial."),
        ("chloe@example.com", 5, "Ultra originale. On sent le travail dans la mise en scène du lieu."),
        ("emma@example.com", 4, "Très haut niveau, peut-être un peu trop premium pour un long séjour."),
        ("farid@example.com", 5, "Les équipements sont excellents et la station a énormément de caractère."),
        ("neil@example.com", 4, "Magnifique, même si le côté lointain de Pluton peut être intimidant."),
    ],
    "Loft Lever de Terre": [
        ("alice@example.com", 5, "Le nom n'est pas mensonger, le panorama est superbe."),
        ("bob@example.com", 4, "Très beau loft, lumineux et pratique."),
        ("david@example.com", 5, "Une des annonces les plus équilibrées entre style et confort."),
        ("farid@example.com", 4, "Bonne surprise, très bien pensé pour un couple."),
        ("luna@example.com", 5, "J'ai adoré la grande baie vitrée et l'ambiance feutrée."),
    ],
    "Cité du Néant": [
        ("alice@example.com", 5, "J’ai adoré le silence du vide autour de la cité. Les passerelles suspendues donnent une vraie sensation d’évasion, et la chambre était parfaite pour se reposer loin de tout."),
        ("bob@example.com", 4, "Très bon séjour. Les grandes salles en purpur sont impressionnantes sans être froides, et la vue sur l’End est incroyable au réveil. Ambiance très reposante."),
        ("chloe@example.com", 5, "Le dôme d’observation est clairement mon endroit préféré. Regarder l’horizon de l’End dans un tel calme, c’est une expérience unique. J’y ai vraiment passé un moment apaisant."),
        ("david@example.com", 3, "Lieu magnifique et très bien entretenu. J’ai surtout apprécié l’isolement et le côté suspendu de la cité, même si le vide tout autour peut surprendre au début."),
        ("emma@example.com", 5, "Excellent repos. Le workshop redstone est bien pensé, mais ce que j’ai préféré, c’est surtout la tranquillité générale du lieu et l’élégance de l’architecture."),
        ("farid@example.com", 4, "Annonce totalement fidèle au lieu. L’accueil du host était discret mais efficace, et les espaces communs sont assez vastes pour se détendre sans jamais se sentir à l’étroit."),
        ("selene@example.com", 5, "Une vraie parenthèse hors du temps. Entre les hauteurs, les couloirs calmes et les lumières douces, tout donne envie de ralentir et de profiter du séjour."),
        ("orion@example.com", 3, "L’endroit est superbe et très dépaysant, mais je cherchais quelque chose d’un peu moins isolé. En revanche, pour quelqu’un qui veut du calme total, c’est idéal."),
    ],
    "Base lunaire Zénith": [
        ("alice@example.com", 5, "Très haut de gamme. Le low gravity gym est une excellente idée."),
        ("bob@example.com", 4, "Séjour premium sans mauvaise surprise."),
        ("chloe@example.com", 5, "Luxueux, propre, bien présenté. Très pratique pour tester un front vitrine."),
        ("david@example.com", 4, "Très bon niveau général, avec une vraie cohérence esthétique."),
        ("emma@example.com", 5, "Le cinéma holographique est top et l'espace nuit est superbe."),
        ("farid@example.com", 4, "Excellente annonce admin, sérieuse et complète."),
        ("neil@example.com", 5, "Clairement une valeur sûre."),
    ],
    "Astéroïde Gamma A45": [
        ("alice@example.com", 4, "Séjour atypique et marquant. Très bonne ambiance."),
        ("bob@example.com", 4, "Minimaliste mais l'idée est géniale."),
        ("chloe@example.com", 5, "J'ai adoré le sentiment d'être coincée dans une roche vivante au milieu de l'espace."),
    ],
    "Refuge Face Cachée": [],
    "Capsule Horizon 9": [
        ("alice@example.com", 3, "Minuscule, mais à ce prix on sait à quoi s'attendre."),
    ],
}


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
    owners_by_title: dict[str, str] = {}
    for place in PLACE_SEED:
        place_id = place["id"]
        places_by_title[place["title"]] = place_id
        owners_by_title[place["title"]] = place["owner_email"]
        cur.execute(
            """
            INSERT INTO places (id, title, description, price, latitude, longitude, owner_id, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                place_id,
                place["title"],
                place["description"],
                place["price"],
                place["latitude"],
                place["longitude"],
                users_by_email[place["owner_email"]],
                ts,
                ts,
            ),
        )
        for amenity_name in place["amenities"]:
            cur.execute(
                "INSERT INTO place_amenity (place_id, amenity_id) VALUES (?, ?)",
                (place_id, amenities_by_name[amenity_name]),
            )

    review_total = 0
    for place_title, review_rows in REVIEW_MAP.items():
        owner_email = owners_by_title[place_title]
        used_reviewers = set()
        for reviewer_email, rating, text in review_rows:
            if reviewer_email == owner_email:
                continue
            if reviewer_email in used_reviewers:
                continue
            used_reviewers.add(reviewer_email)
            cur.execute(
                """
                INSERT INTO reviews (id, text, rating, user_id, place_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    new_id(),
                    text,
                    rating,
                    users_by_email[reviewer_email],
                    places_by_title[place_title],
                    ts,
                    ts,
                ),
            )
            review_total += 1

    conn.commit()

    counts = {
        "users": cur.execute("SELECT COUNT(*) FROM users").fetchone()[0],
        "admins": cur.execute("SELECT COUNT(*) FROM users WHERE is_admin = 1").fetchone()[0],
        "amenities": cur.execute("SELECT COUNT(*) FROM amenities").fetchone()[0],
        "places": cur.execute("SELECT COUNT(*) FROM places").fetchone()[0],
        "reviews": cur.execute("SELECT COUNT(*) FROM reviews").fetchone()[0],
        "place_amenity": cur.execute("SELECT COUNT(*) FROM place_amenity").fetchone()[0],
    }

    print(f"DB generated: {DB_PATH}")
    print(counts)
    print("Accounts:")
    for _, _, email, password, is_admin in USER_SEED:
        print(f"- {email} / {password} / {'admin' if is_admin else 'user'}")
    print("Reviews per place:")
    for place in PLACE_SEED:
        place_title = place["title"]
        count = cur.execute(
            "SELECT COUNT(*) FROM reviews WHERE place_id = ?",
            (places_by_title[place_title],),
        ).fetchone()[0]
        print(f"- {place_title}: {count}")

    conn.close()


if __name__ == "__main__":
    main()
