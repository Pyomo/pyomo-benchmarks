#!/bin/bash -v

set +e

\rm -Rf *master
\rm -Rf *expr_dev

module unload python36
module unload python35
module unload python27
module unload pypy2

module load pypy2
make install

module unload pypy2
module load python36
make install

module unload python36
module load python35
make install

module unload python35
module load python27
make install

