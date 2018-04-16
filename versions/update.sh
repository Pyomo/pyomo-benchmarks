#!/bin/bash -v

set +e

\rm -Rf *master
\rm -Rf *expr_dev

module unload python36
module unload python35
module unload python27
module unload pypy2

module load pypy2
/usr/bin/python install.py

module unload pypy2
module load python36
/usr/bin/python install.py

module unload python36
module load python35
/usr/bin/python install.py

module unload python35
module load python27
/usr/bin/python install.py

