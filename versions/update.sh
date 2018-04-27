#!/bin/bash -v

echo "SKIPPING PYOMO UPDATE"
exit 0

set +e

\rm -Rf *master
\rm -Rf *expr_dev

module unload python36
module unload python35
module unload python27
module unload pypy2

module load pypy2
/usr/bin/python install.py pypy

module unload pypy2
module load python36
/usr/bin/python install.py python3.6 python3.6-cython

module unload python36
module load python35
/usr/bin/python install.py python3.5 python3.5-cython

module unload python35
module load python27
/usr/bin/python install.py python2.7 python2.7-cython

