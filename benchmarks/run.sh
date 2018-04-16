#!/bin/sh
module unload python36
module unload python35
module unload python27
module unload pypy2
module load python27
../versions/python2.7-cython-expr_dev/bin/python expr100000.py expr100000_branches.csv python2.7-cython expr_dev
module unload python27
