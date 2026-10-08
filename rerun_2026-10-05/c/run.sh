#!/bin/sh
cd "$(dirname "$0")"
gcc --version | head -1 > env.txt
sha256sum ../wilf_m23/independent.c >> env.txt
gcc -O3 -std=gnu11 ../wilf_m23/independent.c -o indep
for dm in "3 20" "3 21" "3 22" "3 23" "4 20" "4 21" "4 22" "4 23" "5 20" "5 21" "5 22" "5 23" "6 22" "6 23"; do
  set -- $dm
  ( start=$(date +%s); ./indep $1 $2 $2 > d$1_m$2.log 2> d$1_m$2.err; echo "exit=$? secs=$(( $(date +%s) - start ))" > d$1_m$2.done ) &
done
wait
echo ALLDONE > all.done
