import psycopg2
import time
import os
from dotenv import dotenv_values

# Constants
LOOP_DELAY = 0.2  # seconds

# Global variables
config = None
conn = None
cur = None


def process():
    # Get data
    data = 0  # Placeholder for data

    # Insert sensor data into database
    cur.execute("INSERT INTO samples (data) VALUES (%s)", (data,))
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


if __name__ == "__main__":
    main()
