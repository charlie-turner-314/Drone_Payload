import os
import psycopg2
import time
import asyncio

from dotenv import dotenv_values
from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from threading import Thread, Lock
from io import BytesIO
from PIL import Image
from .dummy import get_imagery_data, Video
from sampling.sampling_tube import extend, retract
from enviro.enviro import get_data as get_enviro_data, display_loop, init_hardware, VideoFeed, video_feed_loop, write_ip_address
import logging
import atexit
import subprocess


# Constants

LOOP_DELAY = 1  # seconds

# Global variables
config = None
conn = None
cur = None
vide_feed = None

tube_state = "retracted"
last_tube_time = None
EXTEND_TIME = 5 # Seconds
TUBE_COOLDOWN = 20 # Seconds

app = Flask(__name__)
CORS(app)

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
    # try to convert to int, if not possible, default to 0
    try:
        start = int(start)
    except ValueError:
        start = 0

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
        # id,
        # valve_state,
        # aruco_id,
        # aruco_pose_x,
        # aruco_pose_y,
        # aruco_pose_z,
        # guage
    try:
        data = cur.fetchone()
    except Exception as e:
        logging.error("Failed to get imagery data: %s", e)
        data = None

    return jsonify(
        error=False,
        data=data,
    )


def video_gen():
    while True:
        frame = video_feed.get_frame()
        if frame:
            try:
                # Assuming 'frame' is a PIL Image. If it's already bytes, adjust accordingly.
                buffer = BytesIO()
                frame.save(buffer, format='JPEG')
                frame_bytes = buffer.getvalue()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
            except Exception as e:
                logging.error("Failed to encode frame: %s", e)
        else:
            logging.warning("No frame available to stream.")
        time.sleep(0.05)  # Adjust the sleep time as needed


@app.route("/video")
def get_video():
    return Response(
        video_gen(),
        mimetype="multipart/x-mixed-replace; boundary=frame"
    )

async def handle_sampling_tube():
    global tube_state
    global last_tube_time
    time_now = time.time()
    if last_tube_time is not None and time_now - last_tube_time < TUBE_COOLDOWN:
        logging.info("Tube is cooling down, skipping")
        return
    tube_state = "extended"
    last_tube_time = time_now
    extend()
    await asyncio.sleep(EXTEND_TIME)
    retract()
    tube_state = "retracted"

def read_all(bme280, ltr559, video_feed:VideoFeed):
    global conn
    global cur

    next_time = time.time() + LOOP_DELAY
    while True:
        time.sleep(max(0, next_time - time.time()))

        # Get data
        enviro = get_enviro_data(bme280, ltr559)
        video_details = video_feed.get_details()
        if not video_details:
            video_details = {}

        pressure = video_details.get("pressure")
        if pressure is not None and pressure < 2 and tube_state == "retracted":
            asyncio.run(handle_sampling_tube())

        # Insert data into database
        cur.execute(
            "INSERT INTO data (temperature, pressure, humidity, light, oxidised, reduced, nh3, valve_state, aruco_id, aruco_pose_x, aruco_pose_y, aruco_pose_z, guage) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (
                enviro.get("temperature"),
                enviro.get("pressure"),
                enviro.get("humidity"),
                enviro.get("light"),
                enviro.get("oxidised"),
                enviro.get("reduced"),
                enviro.get("nh3"),
                video_details.get("valve_state"),
                video_details.get("aruco_id"),
                video_details.get("aruco_pose_x"),
                video_details.get("aruco_pose_y"),
                video_details.get("aruco_pose_z"),
                video_details.get("pressure"),
            )
        )
        conn.commit()

        next_time += (time.time() - next_time) // LOOP_DELAY * LOOP_DELAY + LOOP_DELAY


def main():
    global config
    global conn
    global cur
    global app
    global video_feed

    # Load environment variables
    config = {
        **os.environ,
        **dotenv_values(".env")
    }

    # Initialize database connection
    conn = psycopg2.connect(
        host=config["DB_HOST"],
        database=config["DB_NAME"],
        user=config["DB_USER"],
        password=config["DB_PASS"],
    )
    cur = conn.cursor()

    # Get Hardware Handles
    bme280, ltr559, st7735_display = init_hardware()

    # get video feed handle 
    video_feed = VideoFeed()
    # start video feed thread
    video_thread = Thread(target=video_feed_loop, args=(video_feed,), daemon=True)
    video_thread.start()

    # Start display thread
    display_thread = Thread(target=display_loop, args=(st7735_display, bme280, ltr559, video_feed), daemon=True)
    display_thread.start()

    # Start reading data
    thread = Thread(target=read_all, args=(bme280, ltr559, video_feed), daemon=True)
    thread.start()


    def cleanup_at_exit():
        logging.info("Cleaning up database")
        cur.close()
        conn.close()

        logging.info("Cleaning up Hardware")
        # write the ip address of the pi to the display
        write_ip_address(st7735_display)

    atexit.register(cleanup_at_exit)


    # Start web server
    logging.info("Starting web server")
    app.run(host=config["FLASK_HOST"], port=config["FLASK_PORT"], debug=False)
