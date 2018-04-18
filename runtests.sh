#!/bin/sh -v
#

#
# Test conversions
#
./run --modules --releases --keep convertS > convertS_releases.out 2>&1
./run --modules convertS > convertS_branches.out 2>&1
./summarize convertS
#./run --modules convertL > convertL.out 2>&1
#./summarize convertL

#./run --modules expr100000 > expr100000.out 2>&1
#./summarize expr100000


