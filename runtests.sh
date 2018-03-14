#!/bin/sh
#
# Update installations of Pyomo versions
#
cd versions
./update.sh
cd ..
#
# Test conversions
#
rm benchmarks/convertL_branches.csv
./run --modules --branches convertL > convertL.out 2>&1
cat benchmarks/convertL_branches.csv >> benchmarks/convertL_history.csv

rm benchmarks/expr100000_branches.csv
./run --modules --branches expr100000 > expr100000.out 2>&1
cat benchmarks/expr100000_branches.csv >> benchmarks/expr100000_history.csv


