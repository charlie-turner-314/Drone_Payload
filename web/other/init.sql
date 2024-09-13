CREATE TABLE samples (
    id SERIAL PRIMARY KEY,
    temperature REAL NOT NULL,
    pressure REAL NOT NULL,
    humidity REAL NOT NULL,
    light REAL NOT NULL,
    oxidised REAL NOT NULL,
    reduced REAL NOT NULL,
    nh3 REAL NOT NULL
);
