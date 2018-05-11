#!/bin/sh -v

#echo "SKIPPING RUNTESTS"
#exit 0


#
# Test conversions
#
#./run --modules --releases convertS convert.py --keep > convertS_releases.out 2>&1
#./run --modules convertS convert.py > convertS.out 2>&1
#./summarize convertS

./run --modules --releases convertL convert.py --keep --large > convertL_releases.out 2>&1
./run --modules convertL convert.py --large > convertL.out 2>&1
./summarize convertL

#./run --modules expr100000 > expr100000.out 2>&1
#./summarize expr100000


