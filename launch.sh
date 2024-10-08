#!/bin/bash
source /home/team6/.env/bin/activate

# Function to handle cleanup on exit
cleanup() {
    echo "Cleaning up..."
    # Kill all background processes
    pkill -P $$
    exit 0
}

# Trap SIGINT (Ctrl-C) and call the cleanup function
trap cleanup SIGINT

# Navigate to the web/database directory and start docker compose in the background
(cd web/database && docker compose up) &

# Navigate to the web/frontend directory and run npm in the background
(cd web/frontend && npm run dev -- --host) &

# Run the python script in the background
python main.py &

# Wait for all background processes to finish
wait