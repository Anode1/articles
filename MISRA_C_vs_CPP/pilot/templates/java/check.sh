#!/bin/sh
# builds, then runs both operations on the visible fixtures
set -e
cd "$(dirname "$0")"
javac -d . *.java
java -cp . Bench find fixtures/store.txt Outputs
java -cp . Bench and fixtures/a.txt fixtures/b.txt
