#!/bin/sh
# builds, then runs both operations on the visible fixtures
set -e
cd "$(dirname "$0")"

python3 bench.py find fixtures/store.txt Outputs
python3 bench.py and fixtures/a.txt fixtures/b.txt
