#!/bin/sh
# Builds the path index for the path-with-read run: each key set maps to one document
# path under the project root. The agent recalls a path and reads the document.
set -eu
AIS=${AIS:-$HOME/ais/ais}; IDX=${1:-index}   # the ais binary, built in its checkout
rm -rf "$IDX"; "$AIS" -f "$IDX" --init >/dev/null
s() { "$AIS" -f "$IDX" -v "$@" >/dev/null; }
s doc/deployments/release_runbook.txt  deploy docs release runbook promote uat prod
s doc/deployments/env_install.txt      deploy docs install environment
s doc/deployments/architectures.txt    deploy docs architecture topology
s doc/deployments/eb_monitoring.txt    deploy docs monitoring logs watch
s doc/deployments/db_backup.txt        database db backup restore snapshot
s doc/deployments/performance.txt      performance capacity
s doc/deployments/config_reference.txt config reference
s doc/environments.txt                 environments prod uat addresses ids
s java/release.sh                      release build packaging artifact script
echo "index $IDX: $("$AIS" -f "$IDX" --stats | head -1)"
