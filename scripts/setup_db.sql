-- Run this script as the postgres superuser:
--   psql -U postgres -f scripts/setup_db.sql

-- Create dedicated database user
CREATE USER mehnat_user WITH
    PASSWORD 'shaffofmehnat'
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE;

-- Create the database
CREATE DATABASE mehnat_bot
    WITH
    OWNER = mehnat_user;

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE mehnat_bot TO mehnat_user;

-- Connect to the database and grant schema privileges
\c mehnat_bot
GRANT ALL ON SCHEMA public TO mehnat_user;
GRANT CREATE ON SCHEMA public TO mehnat_user;

-- Enable useful extensions
CREATE EXTENSION IF NOT EXISTS pg_trgm;    -- Trigram fuzzy search (future use)
CREATE EXTENSION IF NOT EXISTS unaccent;   -- Accent-insensitive search (future use)

SELECT 'Database setup complete.' AS status;
