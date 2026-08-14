#!/bin/sh
# atree2s.sh : convert an Ahnentafel number to an atree path  (POSIX sh).
# Usage: atree2s.sh <ahnentafel-number>

my_gender=F          # subject's sex: M or F
male=M
female=F

case "$1" in
    '')        echo "usage: $0 <ahnentafel-number>" >&2; exit 1 ;;
    *[!0-9]*)  echo "$0: '$1' is not a number"      >&2; exit 1 ;;
esac
case "$1" in
    *[!0]*)    : ;;
    *)         echo "$0: Ahnentafel numbers start at 1" >&2; exit 1 ;;
esac

# Ahnentafel number -> binary -> letters (0 = father M, 1 = mother F).
# bc folds long output at 70 columns with a backslash-newline;
# strip the continuations before touching the digits, or paths
# deeper than 67 generations are silently corrupted below.
binary=$(echo "obase=2; $1" | bc | tr -d '\\\n')
letters=$(printf '%s' "$binary" | tr '0' "$male" | tr '1' "$female")

# The leading bit denotes the subject; rewrite it as the subject's sex.
letters=$(printf '%s' "$letters" | sed "s/^./$my_gender/")

echo "$letters"
