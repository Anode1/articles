#!/bin/sh
# builds, then runs both operations on the visible fixtures
set -e
cd "$(dirname "$0")"
cc -O2 -o bench bench.c
./bench find fixtures/store.txt Outputs
./bench and fixtures/a.txt fixtures/b.txt
