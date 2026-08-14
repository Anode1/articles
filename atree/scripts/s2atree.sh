#!/bin/sh
# s2atree.sh : convert an atree path to its Ahnentafel number  (POSIX sh).
# Usage: s2atree.sh <atree-path>

male=M
female=F

case "$1" in
    '')        echo "usage: $0 <atree-path>"        >&2; exit 1 ;;
    *[!MF]*)   echo "$0: '$1' is not an atree path" >&2; exit 1 ;;
esac

# The first letter is the subject; the Ahnentafel leading bit is always 1,
# so normalise it to F before mapping letters back to bits (M = 0, F = 1).
path="$female$(printf '%s' "$1" | cut -c2-)"
binary=$(printf '%s' "$path" | tr "$male" '0' | tr "$female" '1')

echo "ibase=2; $binary" | bc
