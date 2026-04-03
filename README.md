# 🏗 HBnB Evolution

---


## 📑 Table of Contents

- [Overview](#-overview)
- [Project Scope](#1️⃣-project-scope)
- [High-Level Architecture](#2️⃣-high-level-architecture)
- [Business Logic Layer](#3️⃣-business-logic-layer)
- [API Interaction Sequence Diagrams](#4️⃣-api-interaction-sequence-diagrams)
- [Architectural Principles Applied](#5️⃣-architectural-principles-applied)
- [Assumptions & Design Decisions](#6️⃣-assumptions--design-decisions)
- [Conclusion](#7️⃣-conclusion)
- [Part 2 — Implementation](#-part-2--implementation-of-business-logic--rest-api)
- [Part 4 — Front-End Web Client](#-part-4--front-end-web-client)
- [Authors](#-authors)

---

## 📘 Overview

This document provides the complete architectural and technical foundation of the **HBnB Evolution** application.

It consolidates:

- High-level architecture
- Business Logic design
- API interaction sequence diagrams
- Design decisions and applied principles
- Back-end implementation progress
- Front-end web client delivery

The objective is to ensure clarity, strict alignment with project requirements, and readiness for implementation in subsequent phases.

---

## 1️⃣ Project Scope

HBnB Evolution is a simplified AirBnB-like application allowing:

- **User Management** (registration, update, deletion, administrator role)
- **Place Management** (creation, update, deletion, listing)
- **Review Management** (creation, update, deletion, listing by place)
- **Amenity Management** (creation, update, deletion, listing)

The system follows:

- **Layered Architecture**
- **Facade Design Pattern**
- Controlled dependency direction between layers

All entities are uniquely identified using **UUID4** and include audit fields (`created_at`, `updated_at`).

---

## 2️⃣ High-Level Architecture

## 📦 High-Level Package Diagram

<p align="center">
  <img src="./docs/high_level/High_level_package_diagram_HBNB.png" width="900"/>
</p>

<p align="center">
  <a href="./docs/high_level/High_level_package_diagram_HBNB.pdf">📄 View Full PDF Version</a>
</p>

## 🎯 Purpose

This diagram illustrates:

- The three-layer architecture
- Clear separation of responsibilities
- Controlled communication via the Facade pattern

### Layers

### 1️⃣ Presentation Layer (API / Controllers)
- Handles HTTP requests and responses
- Performs input validation
- Delegates use cases to the Facade
- Contains no domain logic

### 2️⃣ Business Logic Layer (Models + Facade)
- Contains domain entities
- Implements business rules
- Coordinates use cases
- Enforces domain integrity

### 3️⃣ Persistence Layer (Repositories)
- Responsible for data storage and retrieval
- Abstracted from business logic
- Ensures database independence

The Presentation Layer communicates exclusively with the Business Logic Layer through the **Facade**.

---

## 3️⃣ Business Logic Layer

## 📊 Class Diagram

<p align="center">
  <img src="./docs/class_diagram/Class_diagram_for_business_Logic_Layer_HBNB.png" width="900"/>
</p>

<p align="center">
  <a href="./docs/class_diagram/Class_diagram_for_business_Logic_Layer_HBNB.pdf">📄 View Full PDF Version</a>
</p>

## 🎯 Purpose

This diagram defines:

- Core domain entities
- Attributes (strictly aligned with requirements)
- Inheritance hierarchy
- Relationships and multiplicities
- Business constraints

---

## 🔑 Core Entities

### BaseModel (Abstract)

Shared attributes for all entities:

- `id: UUID4`
- `created_at: datetime`
- `updated_at: datetime`

Ensures:

- Unique identification
- Audit tracking
- Reusability

---

### User

Attributes:

- `id: UUID4`
- `first_name: str`
- `last_name: str`
- `email: str`
- `password: str`
- `is_admin: bool`
- `created_at: datetime`
- `updated_at: datetime`

Responsibilities:

- Can register, update, and delete profile
- Owns multiple Places
- Writes multiple Reviews

---

### Place

Attributes:

- `id: UUID4`
- `title: str`
- `description: str`
- `price: float`
- `latitude: float`
- `longitude: float`
- `owner_id: UUID4`
- `created_at: datetime`
- `updated_at: datetime`

Responsibilities:

- Belongs to a User
- Can be created, updated, deleted, and listed
- Linked to multiple Amenities
- Receives multiple Reviews

---

### Review

Attributes:

- `id: UUID4`
- `rating: int`
- `comment: str`
- `user_id: UUID4`
- `place_id: UUID4`
- `created_at: datetime`
- `updated_at: datetime`

Responsibilities:

- Linked to a specific User
- Linked to a specific Place
- Can be created, updated, deleted, and listed by place

---

### Amenity

Attributes:

- `id: UUID4`
- `name: str`
- `description: str`
- `created_at: datetime`
- `updated_at: datetime`

Responsibilities:

- Can be created, updated, deleted, and listed
- Associated with multiple Places

---

## 🔗 Cardinalities

- User (1) → (*) Place
- User (1) → (*) Review
- Place (1) → (*) Review
- Place (*) ↔ (*) Amenity

All multiplicities are enforced at the Business Logic Layer.

---

## ⚙ Business Rules

- Each entity must have a unique UUID4 identifier
- All entities track creation and update timestamps
- Rating must be between 1 and 5
- Only registered users can create places
- Only registered users can write reviews
- Each review must reference an existing place
- Each place must reference a valid owner (User)

---

## 4️⃣ API Interaction Sequence Diagrams

---

# SD-01 — User Registration (POST `/users`)

<p align="center">
  <img src="./docs/sequence_diagram/Sequence_SD01_User_Registration.png" width="900"/>
</p>

<p align="center">
  <a href="./docs/sequence_diagram/Sequence_SD01_User_Registration.pdf">📄 View Full PDF Version</a>
</p>

### Flow Summary

1. POST request received
2. Email uniqueness verified
3. User entity created
4. Persisted in database
5. 201 Created returned

---

# SD-02 — Place Creation (POST `/places`)

<p align="center">
  <img src="./docs/sequence_diagram/Sequence_SD02_Place_Creation.png" width="900"/>
</p>

<p align="center">
  <a href="./docs/sequence_diagram/Sequence_SD02_Place_Creation.pdf">📄 View Full PDF Version</a>
</p>

### Flow Summary

1. Authenticated request received
2. Owner existence verified
3. Place entity created
4. Persisted
5. 201 Created returned

---

# SD-03 — Review Submission (POST `/places/{id}/reviews`)

<p align="center">
  <img src="./docs/sequence_diagram/Sequence_SD03_Review_Submission.png" width="900"/>
</p>

<p align="center">
  <a href="./docs/sequence_diagram/Sequence_SD03_Review_Submission.pdf">📄 View Full PDF Version</a>
</p>

### Flow Summary

1. Place existence verified
2. User existence verified
3. Rating validated (1–5)
4. Review persisted
5. 201 Created returned

---

# SD-04 — Fetching Places (GET `/places`)

<p align="center">
  <img src="./docs/sequence_diagram/Sequence_SD04_Fetching_Places.png" width="900"/>
</p>

<p align="center">
  <a href="./docs/sequence_diagram/Sequence_SD04_Fetching_Places.pdf">📄 View Full PDF Version</a>
</p>

### Flow Summary

1. GET request received
2. Filters applied
3. Data retrieved from persistence layer
4. 200 OK returned

---

## 5️⃣ Architectural Principles Applied

- Layered Architecture
- Separation of Concerns
- Facade Pattern
- Dependency Direction Control
- Database Isolation
- BaseModel abstraction
- UUID-based identification

---

## 6️⃣ Assumptions & Design Decisions

## Assumptions

- Passwords are assumed to be securely hashed before persistence.
- Authentication mechanism is not detailed in this phase.
- Database implementation will be completed in Part 3.
- Repository layer abstracts storage implementation.

## Design Decisions

- UUID4 ensures global uniqueness.
- Audit fields are centralized in BaseModel.
- Facade centralizes orchestration.
- Entities encapsulate validation logic.

---

## 7️⃣ Conclusion

This document defines the structural and architectural foundation of HBnB Evolution.

It ensures:

- Maintainability
- Scalability
- Business rule traceability
- Strict alignment with project requirements

This documentation will guide implementation in the next phases.

---

## 🔄 Part 2 — Implementation of Business Logic & REST API

## 📌 Overview

After completing the architectural design in **Part 1**, this phase focuses on transforming the documented architecture into a fully functional application.

The objective of Part 2 is to implement:

- The **Business Logic layer**
- The **Presentation layer (REST API with Flask + flask-restx)**
- An **in-memory persistence system**
- The **Facade pattern** for clean layer communication

Authentication (JWT) and database persistence (SQLAlchemy) will be implemented in **Part 3**.

---

### 🏗 Global Architecture (Part 2)

The application now follows a strict modular architecture:

```
Presentation Layer (API - Flask / flask-restx)
        ↓
Facade
        ↓
Business Logic Layer (Models & Relationships)
        ↓
Persistence Layer (In-Memory Repository)
```

### Layer Responsibilities

| Layer | Responsibility |
|--------|---------------|
| Presentation | Define REST endpoints & API documentation |
| Facade | Simplify communication between API and Business Logic |
| Business Logic | Define entities, relationships, validation rules |
| Persistence | Store objects in memory (temporary storage) |

---

### 🧠 Key Concepts Implemented

## 1️⃣ In-Memory Persistence

Instead of using a database at this stage:

- All entities are stored in memory
- Repository handles:
  - Object storage
  - Retrieval
  - Validation
  - Updates

This repository is designed to be **replaced later by SQLAlchemy in Part 3** without modifying the API layer.

---

## 2️⃣ Facade Pattern

The Facade acts as a simplified interface between:

- API endpoints
- Business Logic layer

Instead of letting the API manipulate models directly, the API communicates through:

```
facade.create_user()
facade.get_user()
facade.update_user()
...
```

This ensures:

- Separation of concerns
- Maintainability
- Easier future extension (JWT, DB, RBAC)

---

### 🧱 Business Logic Implementation (T1)

## Core Entities Implemented

- `User`
- `Place`
- `Review`
- `Amenity`

Each entity:

- Inherits common attributes from a base model:
  - `id (UUID)`
  - `created_at`
  - `updated_at`
- Implements validation logic
- Defines relationships with other entities

### Relationships

- A `User` can own multiple `Places`
- A `Place` belongs to one `User`
- A `Place` can have multiple `Amenities`
- A `Place` can have multiple `Reviews`
- A `Review` is linked to:
  - one `User`
  - one `Place`

Validation includes:

- Price validation
- Latitude / Longitude validation
- Required attributes
- Review text validation
- Association integrity

---

### 🌐 API Endpoints Implementation

Base prefix:

```
/api/v1/
```

---

## 👤 Users (T2)

Implemented:

- `POST /users`
- `GET /users`
- `GET /users/<id>`
- `PUT /users/<id>`

Not implemented:

- ❌ DELETE

Password is never returned in API responses.

---

## 🏷 Amenities (T3)

Implemented:

- `POST /amenities`
- `GET /amenities`
- `GET /amenities/<id>`
- `PUT /amenities/<id>`

---

## 🏠 Places (T4)

Implemented:

- `POST /places`
- `GET /places`
- `GET /places/<id>`
- `PUT /places/<id>`

Validation includes:

- `price`
- `latitude`
- `longitude`

Owner and amenities are included when retrieving a place.

---

## ⭐ Reviews (T5)

Implemented:

- `POST /reviews`
- `GET /reviews`
- `GET /reviews/<id>`
- `PUT /reviews/<id>`
- `DELETE /reviews/<id>`

Retrieve all reviews for a specific place supported.

---

### 🧪 Testing & Validation (T6)

Includes:

- cURL testing
- Swagger documentation (flask-restx)
- Attribute validation
- Edge case handling
- Automated tests (unittest / pytest)

---

### 🚀 Project Scope Status

| Part | Status |
|------|--------|
| Part 1 | Architecture & UML Design |
| Part 2 | Business Logic + REST API (In-Memory) |
| Part 3 | SQLAlchemy + JWT + RBAC |
| Part 4 | Front-End Web Client |

---

### 📂 Repository Structure (Part 2)

```
part2/
│
├── api/
│   └── v1/
│       ├── users.py
│       ├── places.py
│       ├── reviews.py
│       └── amenities.py
│
├── models/
│   ├── base_model.py
│   ├── user.py
│   ├── place.py
│   ├── review.py
│   └── amenity.py
│
├── persistence/
│   └── repository.py
│
├── services/
│   └── facade.py
│
└── run.py
```

---

## 💻 Part 4 — Front-End Web Client

## 📌 Overview

Part 4 adds the browser client for **HBnB Evolution**.
This layer provides a user-facing interface built with **HTML**, **CSS**, and **vanilla JavaScript**, connected to the REST API exposed by the previous parts.

The objective of Part 4 is to make the application usable from a browser by implementing:

- user authentication from a login page
- dynamic listing of places
- price-based filtering
- place detail display
- review creation, edition, and deletion

---

### 🧱 Front-End Pages

Implemented:

- `index.html` for the places list
- `login.html` for authentication
- `place.html` for detailed place information
- `add_review.html` for creating a review
- `edit_review.html` for updating or deleting a review

---

### ⚙ Front-End JavaScript Modules

- `main.js` initializes page-specific behavior
- `auth.js` manages login, logout, and token handling
- `places.js` fetches places, displays cards, filters by price, and renders place details
- `reviews.js` fetches and manages reviews, including add/edit/delete flows
- `utils.js` provides cookie and URL helpers

---

### 🌐 API Integration

The front-end consumes the API under:

```text
http://127.0.0.1:5000/api/v1/
```

Main endpoints used:

- `POST /auth/login`
- `GET /places/`
- `GET /places/<id>`
- `GET /places/<id>/reviews`
- `GET /users/<id>`
- `GET /reviews/<id>`
- `POST /reviews/`
- `PUT /reviews/<id>`
- `DELETE /reviews/<id>`

Authentication is handled with a JWT access token stored in browser cookies and sent through the `Authorization: Bearer <token>` header.

---

### ▶ Running Part 4

Start the back-end API first, then serve the front-end locally:

```bash
cd part4/hbnb
python3 -m http.server 8000
```

Open:

```text
http://127.0.0.1:8000/index.html
```

---

### 📂 Repository Structure (Part 4)

```text
part4/
├── README.md
├── AUTHORS
└── hbnb/
    ├── index.html
    ├── login.html
    ├── place.html
    ├── add_review.html
    ├── edit_review.html
    ├── scripts/
    ├── styles/
    └── images/
```

---

## 👥 Authors

- Antoine Gousset – GitHub: [Antgst](https://github.com/Antgst)
- Gwendal Boisard – GitHub: [Gwendal-B](https://github.com/Gwendal-B)
- Yonas Houriez – GitHub: [Ausaryu](https://github.com/Ausaryu)

See `AUTHORS`.

---
