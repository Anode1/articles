#!/bin/sh
# builds, then runs both operations on the visible fixtures
set -e
cd "$(dirname "$0")"
rustc -O bench.rs -o bench
./bench find fixtures/store.txt Outputs
./bench and fixtures/a.txt fixtures/b.txt
