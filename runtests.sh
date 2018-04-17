#!/bin/sh -v
#

#
# Test conversions
#
./run --modules convertS > convertS.out 2>&1
./summarize convertS
#./run --modules convertL > convertL.out 2>&1
#./summarize convertL

#./run --modules expr100000 > expr100000.out 2>&1
#./summarize expr100000


