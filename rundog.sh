#!/bin/sh

#echo "SKIPPING RUNDOG"
#exit 0

mkdir -p results

./dog 14 convertL
mv dog14.pdf results/convertL_dog14.pdf

./dog 13 convertL
mv dog13.pdf results/convertL_dog13.pdf

./dog 12 convertL
mv dog12.pdf results/convertL_dog12.pdf

./dog 15 convertL
mv dog15.csv results/convertL_dog15.csv

./dog 16 convertL
mv dog16.csv results/convertL_dog16.csv

./dog 20 convertL
mv dog20.pdf results/convertL_dog20.pdf

