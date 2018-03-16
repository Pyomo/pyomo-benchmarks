#!/bin/sh -v
#
# Update installations of Pyomo versions
#
cd versions
./update.sh
cd ..
#
# Test conversions
#
./run --modules convertL > convertL.out 2>&1
./summarize convertL

./run --modules expr100000 > expr100000.out 2>&1
./summarize expr100000


