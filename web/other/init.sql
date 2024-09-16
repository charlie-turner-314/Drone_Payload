CREATE TABLE enviro (
    id SERIAL PRIMARY KEY,
    temperature REAL NOT NULL,
    pressure REAL NOT NULL,
    humidity REAL NOT NULL,
    light REAL NOT NULL,
    oxidised REAL NOT NULL,
    reduced REAL NOT NULL,
    nh3 REAL NOT NULL
);

CREATE TABLE imagery (
    id SERIAL PRIMARY KEY,
    valve_state BOOLEAN,
    aruco_id INTEGER,
    aruco_pose_x REAL,
    aruco_pose_y REAL,
    pressure REAL
);