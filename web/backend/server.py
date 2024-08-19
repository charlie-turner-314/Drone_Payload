import psycopg2
import time
import os
from dotenv import dotenv_values

from enviro.enviro_logging import get_data

# Constants
LOOP_DELAY = 1  # seconds

# Global variables
config = None
conn = None
cur = None


def process():
    # Get data
    enviro = get_data()

    # Insert sensor data into database
    cur.execute("INSERT INTO samples (temperature, pressure, humidity, light, oxidised, reduced, nh3) VALUES (%s, %s, %s, %s, %s, %s, %s)", enviro)
    conn.commit()


def main():
    global config
    global conn
    global cur

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

    # Loop forever
    next_time = time.time() + LOOP_DELAY
    while True:
        time.sleep(max(0, next_time - time.time()))
        process()
        next_time += (time.time() - next_time) // LOOP_DELAY * LOOP_DELAY + LOOP_DELAY
