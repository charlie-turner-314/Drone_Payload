import os
import psycopg2
import time

from dotenv import dotenv_values
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from threading import Thread

from .dummy import get_enviro_data, get_imagery_data, Video
# from enviro.enviro_logging import get_data as get_enviro_data

# Constants
LOOP_DELAY = 1  # seconds

# Global variables
config = None
conn = None
cur = None
running = True

app = Flask(__name__)
cors = CORS(app)
app.config["CORS_HEADERS"] = "Content-Type"


@app.errorhandler(404)
def page_not_found(e):
    return jsonify(
        error=True,
        data="Page not found",
    )


@app.route("/test")
def get_test():
    return jsonify(
        error=False,
        data="Success",
    )


@app.route("/data/all")
def get_all():
    global cur

    limit = request.args.get("limit", 50)

    cur.execute("SELECT * FROM data ORDER BY id DESC LIMIT %s", (limit,))
    data = cur.fetchall()

    return jsonify(
        error=False,
        data=data,
    )


@app.route("/data/enviro")
def get_enviro():
    global cur

    start = request.args.get("start", 0)

    cur.execute("SELECT * FROM enviro WHERE id > %s ORDER BY id ASC", (start,))
    data = cur.fetchall()

    return jsonify(
        error=False,
        data=data,
    )


@app.route("/data/imagery")
def get_imagery():
    global cur

    cur.execute("SELECT * FROM imagery ORDER BY id DESC LIMIT 1")
    data = cur.fetchone()

    return jsonify(
        error=False,
        data=data,
    )


def video_gen(video):
    while True:
        frame = video.get_frame()
        if frame is None:
            break
        yield (b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + frame + b"\r\n")


@app.route("/video")
def get_video():
    return Response(
        video_gen(Video()), mimetype="multipart/x-mixed-replace; boundary=frame"
    )


def read_all():
    global conn
    global cur
    global running

    next_time = time.time() + LOOP_DELAY
    while running:
        time.sleep(max(0, next_time - time.time()))

        # Get data
        enviro = get_enviro_data()
        imagery = get_imagery_data()

        # Insert data into database
        cur.execute(
            "INSERT INTO data (temperature, pressure, humidity, light, oxidised, reduced, nh3, valve_state, aruco_id, aruco_pose_x, aruco_pose_y, guage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (*enviro, *imagery),
        )
        conn.commit()

        next_time += (time.time() - next_time) // LOOP_DELAY * LOOP_DELAY + LOOP_DELAY


def main():
    global config
    global conn
    global cur
    global running
    global app

    # Load environment variables
    config = {
        **dotenv_values(".env"),
        **os.environ,
    }

    # Initialize database connection
    conn = psycopg2.connect(
        host=config["DB_HOST"],
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
    )
    cur = conn.cursor()

    # Start reading data
    thread = Thread(target=read_all)
    thread.start()

    # Start web server
    app.run(host=config["FLASK_HOST"], port=config["FLASK_PORT"], debug=True)

    # Cleanup
    running = False
    thread.join()
