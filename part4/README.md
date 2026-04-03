# HBnB Evolution - Part 4

## Overview

Cette partie 4 correspond au front-end web de HBnB Evolution.
Le dossier contient une interface en HTML, CSS et JavaScript vanilla qui consomme l'API REST du projet pour :

- afficher la liste des places disponibles
- filtrer les places par prix
- afficher le détail d'une place
- authentifier un utilisateur
- ajouter, modifier et supprimer un avis

L'interface s'appuie sur des modules JavaScript séparés pour l'authentification, les places, les reviews et les utilitaires.

## Main Features

- `login.html` : connexion utilisateur et stockage du token dans les cookies
- `index.html` : affichage dynamique des places et filtre par prix
- `place.html` : détail d'une place, galerie d'images, liste des reviews
- `add_review.html` : création d'un avis avec notation par étoiles
- `edit_review.html` : modification ou suppression d'un avis existant

## Project Structure

```text
part4/
├── README.md
└── hbnb/
    ├── index.html
    ├── login.html
    ├── place.html
    ├── add_review.html
    ├── edit_review.html
    ├── scripts/
    │   ├── main.js
    │   ├── auth.js
    │   ├── places.js
    │   ├── reviews.js
    │   └── utils.js
    ├── styles/
    │   ├── global.css
    │   ├── layout.css
    │   ├── components.css
    │   └── pages/
    └── images/
```

## JavaScript Modules

- `main.js` : point d'entrée, détecte la page courante et initialise les bons comportements
- `auth.js` : gestion du login, du logout et de l'état d'authentification
- `places.js` : récupération, affichage et filtrage des places, détail et galerie
- `reviews.js` : récupération, affichage, création, édition et suppression des reviews
- `utils.js` : lecture des cookies et récupération des paramètres d'URL

## API Endpoints Used

Le front attend une API disponible localement sur :

```text
http://127.0.0.1:5000/api/v1/
```

Endpoints utilisés :

- `POST /auth/login`
- `GET /places/`
- `GET /places/<place_id>`
- `GET /places/<place_id>/reviews`
- `GET /users/<user_id>`
- `GET /reviews/<review_id>`
- `POST /reviews/`
- `PUT /reviews/<review_id>`
- `DELETE /reviews/<review_id>`

## Authentication Flow

1. L'utilisateur se connecte via `login.html`.
2. L'API renvoie un `access_token`.
3. Le token est stocké dans un cookie `token`.
4. Les requêtes protégées envoient `Authorization: Bearer <token>`.
5. Le bouton `Logout` supprime le cookie et redirige vers l'accueil.

## How to Run

Le back-end doit être lancé avant le front.

Depuis la racine du projet :

```bash
cd part4/hbnb
python3 -m http.server 8000
```

Puis ouvrir dans le navigateur :

```text
http://127.0.0.1:8000/index.html
```

## Notes

- Les images des places sont chargées depuis `images/places/<place_id>/`.
- Le front repose sur les paramètres d'URL, par exemple `place.html?id=<place_id>`.
- Certaines actions, comme l'ajout ou l'édition d'un avis, nécessitent un utilisateur authentifié.

## Authors

Yonas Houriez <yonas.houriez@gmail.com>
