-- FoodScout AI Database Schema
-- PostgreSQL

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Restaurants table
CREATE TABLE IF NOT EXISTS restaurants (
    id              UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name            VARCHAR(255) NOT NULL,
    city            VARCHAR(100) NOT NULL,
    area            VARCHAR(100),
    google_rating   DECIMAL(2,1),
    review_count    INTEGER DEFAULT 0,
    speciality      TEXT,
    source_type     VARCHAR(50),
    source_url      TEXT,
    youtube_channel VARCHAR(255),
    google_maps_link TEXT,
    confidence_score INTEGER DEFAULT 0,
    created_at      TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Scan history table
CREATE TABLE IF NOT EXISTS scan_history (
    id                  UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    city                VARCHAR(100) NOT NULL,
    food_category       VARCHAR(100),
    sources_scanned     TEXT[],
    restaurants_found   INTEGER DEFAULT 0,
    scan_time           DECIMAL(10,2),
    status              VARCHAR(50) DEFAULT 'pending',
    task_id             VARCHAR(255),
    error_message       TEXT,
    created_at          TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_restaurants_city ON restaurants(city);
CREATE INDEX IF NOT EXISTS idx_restaurants_confidence ON restaurants(confidence_score DESC);
CREATE INDEX IF NOT EXISTS idx_restaurants_created ON restaurants(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_scan_history_city ON scan_history(city);
CREATE INDEX IF NOT EXISTS idx_scan_history_created ON scan_history(created_at DESC);

-- Unique constraint to help with deduplication
CREATE UNIQUE INDEX IF NOT EXISTS idx_restaurants_name_city 
    ON restaurants(LOWER(name), LOWER(city));
