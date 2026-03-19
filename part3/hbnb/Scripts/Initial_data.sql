-- =============================================================================
-- HBnB — Initial Data
-- Run AFTER schema.sql
-- =============================================================================

-- -----------------------------------------------------------------------------
-- ADMINISTRATOR USER
-- id       : 36c9050e-ddd3-4c3b-9731-9f487208bbc1  (fixed, as required)
-- email    : admin@hbnb.io
-- password : admin1234  →  bcrypt2 hash below
--
-- Hash generated with Python:
--   import bcrypt
--   bcrypt.hashpw(b"admin1234", bcrypt.gensalt()).decode()
-- -----------------------------------------------------------------------------
INSERT INTO users (id, first_name, last_name, email, password, is_admin)
VALUES (
    '36c9050e-ddd3-4c3b-9731-9f487208bbc1',
    'Admin',
    'HBnB',
    'admin@hbnb.io',
    '$2b$12$uEBHs3MpPsEMTkouANxwJ.4s1QHFDpJ8sUGAmgB5e5K9MNqMkJxkS',
    TRUE
);

-- -----------------------------------------------------------------------------
-- INITIAL AMENITIES
-- UUIDs generated with Python: import uuid; uuid.uuid4()
-- -----------------------------------------------------------------------------
INSERT INTO amenities (id, name) VALUES
    ('9f17bfdd-36f3-40b9-b4b7-3a09a96ea9c5', 'WiFi'),
    ('a57e9ed8-f74d-4337-919d-94caf9968897', 'Swimming Pool'),
    ('2ac77957-57c3-4404-9f0b-0a28811a3119', 'Air Conditioning');
