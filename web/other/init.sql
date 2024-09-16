CREATE TABLE data (
    id SERIAL PRIMARY KEY,
    temperature REAL NOT NULL,
    pressure REAL NOT NULL,
    humidity REAL NOT NULL,
    light REAL NOT NULL,
    oxidised REAL NOT NULL,
    reduced REAL NOT NULL,
    nh3 REAL NOT NULL,
    valve_state BOOLEAN,
    aruco_id INTEGER,
    aruco_pose_x REAL,
    aruco_pose_y REAL,
    guage REAL,
    time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE VIEW enviro AS
    SELECT
        id,
        temperature,
        pressure,
        humidity,
        light,
        oxidised,
        reduced,
        nh3
    FROM data;

CREATE VIEW imagery AS
    SELECT
        id,
        valve_state,
        aruco_id,
        aruco_pose_x,
        aruco_pose_y,
        guage
    FROM data;