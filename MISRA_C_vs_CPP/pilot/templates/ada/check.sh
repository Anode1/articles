#!/bin/sh
# builds, then runs both operations on the visible fixtures
set -e
cd "$(dirname "$0")"
mkdir -p obj && gnatmake -q -O2 -D obj -o bench bench.adb
./bench find fixtures/store.txt Outputs
./bench and fixtures/a.txt fixtures/b.txt
