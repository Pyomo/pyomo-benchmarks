#!/bin/sh

#echo "SKIPPING RUNDOG"
#exit 0

mkdir -p results
\rm results/*

./versions/python3.6-master/bin/python dog2 22 convertL # ADD BRANCHES HERE

exit 0

./dog 13 convertL
mv dog13.pdf results/convertL_dog13.pdf

./dog 12 convertL
mv dog12.pdf results/convertL_dog12.pdf

#./dog 14 convertL
#mv dog14.pdf results/convertL_dog14.pdf

#./dog 15 convertL
#mv dog15.csv results/convertL_dog15.csv

#./dog 16 convertL
#mv dog16.csv results/convertL_dog16.csv

./dog 21 convertL
mv dog21_pypy.pdf results/convertL_dog21_pypy.pdf
mv dog21_python2.7.pdf results/convertL_dog21_python2.7.pdf
mv dog21_python3.6.pdf results/convertL_dog21_python3.6.pdf

./dog 22 convertL expr_not_variable expr_wo_asnumeric # ADD BRANCHES HERE
mv dog22_pypy.pdf results/convertL_dog22_pypy.pdf
mv dog22_python2.7.pdf results/convertL_dog22_python2.7.pdf
mv dog22_python3.6.pdf results/convertL_dog22_python3.6.pdf

./dog 23 convertL expr_not_variable expr_wo_asnumeric # ADD BRANCHES HERE
mv dog23_pypy.pdf results/convertL_dog23_pypy.pdf
mv dog23_python2.7.pdf results/convertL_dog23_python2.7.pdf
mv dog23_python3.6.pdf results/convertL_dog23_python3.6.pdf


