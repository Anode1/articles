#!/bin/sh
set -eu
S=$(dirname "$0"); cd "$S"
IAC=$HOME/iac/iac
gcc -O2 -o bench_wake bench_wake.c
out=results.csv; echo "fs,mode,base_size,iter,send_ms,wake_ms" > $out
for fs in ext4 tmpfs; do
  case $fs in ext4) base=$S/rooms;; tmpfs) base=/dev/shm/iacbench;; esac
  rm -rf "$base"; mkdir -p "$base"
  for mb in 0 1 100; do
    room=$base/r$mb; mkdir -p $room
    $IAC join $room bob >/dev/null
    python3 -I mklog.py $room/log $((mb*1024*1024)) >/dev/null
    size=$(stat -c %s $room/log)
    # the log and cursor must be readable: warm the page cache once
    cat $room/log >/dev/null
    ./bench_wake $IAC $room $size wake 300 | sed "s/^/$fs,/" >> $out
    if [ $mb -gt 0 ]; then ./bench_wake $IAC $room $size catchup 30 | sed "s/^/$fs,/" >> $out; fi
  done
done
rm -rf /dev/shm/iacbench
echo DONE
