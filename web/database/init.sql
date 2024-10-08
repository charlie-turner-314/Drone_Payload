CREATE TABLE data (
    id SERIAL PRIMARY KEY,
    temperature REAL,
    pressure REAL,
    humidity REAL,
    light REAL,
    oxidised REAL,
    reduced REAL,
    nh3 REAL,
    valve_state BOOLEAN,
    aruco_id INTEGER,
    aruco_pose_x REAL,
    aruco_pose_y REAL,
    aruco_pose_z REAL,
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
        aruco_pose_z,
        guage
    FROM data;
