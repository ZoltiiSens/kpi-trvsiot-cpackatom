CREATE TABLE processed_agent_data (
    id SERIAL PRIMARY KEY,
    road_state VARCHAR(255) NOT NULL,
    x FLOAT,
    y FLOAT,
    z FLOAT,
    latitude FLOAT,
    longitude FLOAT,
    peak BOOLEAN,
    pit BOOLEAN,
    timestamp TIMESTAMP
);