#!/usr/bin/env bash

# Start the FastAPI server, wait for it to become ready, run backend tests,
# and then shut down the server.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
SERVER_LOG="$ROOT_DIR/server_test.log"

cd "$BACKEND_DIR"
uvicorn server:app --reload --host 0.0.0.0 --port 8001 > "$SERVER_LOG" 2>&1 &
SERVER_PID=$!
cd "$ROOT_DIR"

cleanup() {
    echo "Stopping backend server..."
    kill "$SERVER_PID" 2>/dev/null || true
    wait "$SERVER_PID" 2>/dev/null || true
}
trap cleanup EXIT

echo -n "Waiting for backend server to start"
for i in {1..30}; do
    if curl -s http://localhost:8001/api/health > /dev/null; then
        echo " - ready"
        break
    fi
    echo -n "."
    sleep 1
    if [ "$i" -eq 30 ]; then
        echo "\nBackend server did not start in time" >&2
        exit 1
    fi
done

python backend_test.py
EXIT_CODE=$?
exit $EXIT_CODE
