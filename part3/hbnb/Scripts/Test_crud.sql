-- =============================================================================
-- HBnB — CRUD Test Script
-- Run AFTER schema.sql + initial_data.sql
-- =============================================================================

-- =============================================================================
-- READ — verify initial data
-- =============================================================================

SELECT id, first_name, last_name, email, is_admin FROM users;

SELECT id, name FROM amenities;

-- =============================================================================
-- CREATE
-- =============================================================================

-- Insert a regular user
INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES (
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
    'John',
    'Doe',
    'john.doe@example.com',
    '$2b$12$placeholder_hash_for_test',
    FALSE
);

-- Insert a place owned by the regular user
INSERT INTO places (id, title, description, price, latitude, longitude, owner_id)
VALUES (
    'cccccccc-cccc-cccc-cccc-cccccccccccc',
    'Cozy Apartment',
    'A nice place in the city center',
    75.00,
    48.8566,
    2.3522,
    'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb'
);

-- Link amenities to the place (many-to-many)
INSERT INTO place_amenity (place_id, amenity_id) VALUES
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '9f17bfdd-36f3-40b9-b4b7-3a09a96ea9c5'),
    ('cccccccc-cccc-cccc-cccc-cccccccccccc', '2ac77957-57c3-4404-9f0b-0a28811a3119');

-- Insert a review left by the admin on the place
INSERT INTO reviews (id, text, rating, user_id, place_id)
VALUES (
    'dddddddd-dddd-dddd-dddd-dddddddddddd',
    'Very comfortable and well located!',
    5,
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'cccccccc-cccc-cccc-cccc-cccccccccccc'
);

-- =============================================================================
-- READ — relational queries
-- =============================================================================

-- All places with owner name
SELECT p.id, p.title, p.price, u.first_name, u.last_name
FROM places p
JOIN users u ON p.owner_id = u.id;

-- All reviews for a place with reviewer info
SELECT r.rating, r.text, u.first_name, u.last_name
FROM reviews r
JOIN users u ON r.user_id = u.id
WHERE r.place_id = 'cccccccc-cccc-cccc-cccc-cccccccccccc';

-- All amenities for a place (many-to-many join)
SELECT p.title, a.name AS amenity
FROM places p
JOIN place_amenity pa ON p.id = pa.place_id
JOIN amenities a      ON a.id = pa.amenity_id
WHERE p.id = 'cccccccc-cccc-cccc-cccc-cccccccccccc';

-- =============================================================================
-- UPDATE
-- =============================================================================

UPDATE places
SET price = 90.00
WHERE id = 'cccccccc-cccc-cccc-cccc-cccccccccccc';

UPDATE reviews
SET text = 'Excellent stay, would come back!', rating = 5
WHERE id = 'dddddddd-dddd-dddd-dddd-dddddddddddd';

-- Verify updates
SELECT id, title, price FROM places WHERE id = 'cccccccc-cccc-cccc-cccc-cccccccccccc';
SELECT id, text, rating  FROM reviews WHERE id = 'dddddddd-dddd-dddd-dddd-dddddddddddd';

-- =============================================================================
-- CONSTRAINT TESTS (uncomment to verify violations are rejected)
-- =============================================================================

-- Duplicate email → UNIQUE constraint on users.email
INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES ('eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee', 'Jane', 'Doe', 'john.doe@example.com', 'hash', FALSE);

-- Duplicate review (same user + same place) → UNIQUE(user_id, place_id)
INSERT INTO reviews (id, text, rating, user_id, place_id)
VALUES ('ffffffff-ffff-ffff-ffff-ffffffffffff', 'Second review', 3,
         '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
         'cccccccc-cccc-cccc-cccc-cccccccccccc');

-- Invalid rating → CHECK(rating BETWEEN 1 AND 5)
INSERT INTO reviews (id, text, rating, user_id, place_id)
VALUES ('aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa', 'Bad rating', 6,
        'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb',
        'cccccccc-cccc-cccc-cccc-cccccccccccc');

-- =============================================================================
-- DELETE
-- =============================================================================

--DELETE FROM reviews WHERE id = 'dddddddd-dddd-dddd-dddd-dddddddddddd';

--DELETE FROM places WHERE id = 'cccccccc-cccc-cccc-cccc-cccccccccccc';

--DELETE FROM users WHERE id = 'bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb';

-- Final state: only admin and the 3 amenities remain
SELECT id, email, is_admin FROM users;
SELECT id, name FROM amenities;
