-- =============================================================================
-- HBnB — Database Schema
-- Compatible: MySQL / SQLite
-- =============================================================================

-- Drop tables in reverse dependency order
DROP TABLE IF EXISTS place_amenity;
DROP TABLE IF EXISTS reviews;
DROP TABLE IF EXISTS places;
DROP TABLE IF EXISTS amenities;
DROP TABLE IF EXISTS users;

-- =============================================================================
-- TABLE: users
-- =============================================================================
CREATE TABLE users (
    id         CHAR(36)     NOT NULL PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name  VARCHAR(255) NOT NULL,
    email      VARCHAR(255) NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    is_admin   BOOLEAN      NOT NULL DEFAULT FALSE
);

-- =============================================================================
-- TABLE: amenities
-- =============================================================================
CREATE TABLE amenities (
    id   CHAR(36)     NOT NULL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

-- =============================================================================
-- TABLE: places
-- =============================================================================
CREATE TABLE places (
    id          CHAR(36)       NOT NULL PRIMARY KEY,
    title       VARCHAR(255)   NOT NULL,
    description TEXT,
    price       DECIMAL(10, 2) NOT NULL,
    latitude    FLOAT          NOT NULL,
    longitude   FLOAT          NOT NULL,
    owner_id    CHAR(36)       NOT NULL,
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

-- =============================================================================
-- TABLE: reviews
-- =============================================================================
CREATE TABLE reviews (
    id       CHAR(36) NOT NULL PRIMARY KEY,
    text     TEXT     NOT NULL,
    rating   INT      NOT NULL CHECK (rating BETWEEN 1 AND 5),
    user_id  CHAR(36) NOT NULL,
    place_id CHAR(36) NOT NULL,
    FOREIGN KEY (user_id)  REFERENCES users(id),
    FOREIGN KEY (place_id) REFERENCES places(id),
    UNIQUE (user_id, place_id)
);

-- =============================================================================
-- TABLE: place_amenity  (many-to-many)
-- =============================================================================
CREATE TABLE place_amenity (
    place_id   CHAR(36) NOT NULL,
    amenity_id CHAR(36) NOT NULL,
    PRIMARY KEY (place_id, amenity_id),
    FOREIGN KEY (place_id)   REFERENCES places(id),
    FOREIGN KEY (amenity_id) REFERENCES amenities(id)
);
