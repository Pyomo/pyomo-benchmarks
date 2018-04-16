#
# Install different versions of Pyomo on different versions
# of Python.
#
import sys
import subprocess
import os
import shutil
import csv

using_modules = True

version = ['pypy',
'python3.6', 
'python3.6-cython',
'python3.5', 
'python3.5-cython',
'python2.7', 
'python2.7-cython'
]

config = {
'python3.6':
{
'pyomo_version':    ['5.2', '5.3', '5.4.3', '-master', '-expr_dev'],
'pyutilib_version': ['5.5', '5.6', '5.6.2', '5.6.2',   '5.6.2']
},
'python3.6-cython':
{
'pyomo_version':    ['-expr_dev'],
'pyutilib_version': ['5.6.2']
},
'python3.5':
{
'pyomo_version':    ['5.1.1', '5.2', '5.3', '5.4.3', '-master', '-expr_dev'],
'pyutilib_version': ['5.4.1', '5.5', '5.6', '5.6.2', '5.6.2',   '5.6.2']
},
'python3.5-cython':
{
'pyomo_version':    ['-expr_dev'],
'pyutilib_version': ['5.6']
},
'python2.7':
{
'pyomo_version':    ['4.1.10527', '4.2.10784', '4.3.11388', '4.4.1', '5.0', '5.1.1', '5.2', '5.3', '5.4.3', '-master', '-expr_dev'],
'pyutilib_version': ['5.1.3556',  '5.2.3601',  '5.3.5',     '5.4',   '5.4', '5.4.1', '5.5', '5.6', '5.6.2', '5.6.2',   '5.6.2']
},
'python2.7-cython':
{
'pyomo_version':    ['-expr_dev'],
'pyutilib_version': ['5.6.2']
},
'pypy':
{
'pyomo_version':    ['5.0', '5.1.1', '5.2', '5.3', '5.4.3', '-master', '-expr_dev'],
'pyutilib_version': ['5.4', '5.4.1', '5.5', '5.6', '5.6.2', '5.6.2',   '5.6.2']
}
}


#[['directory', 'python', 'pyomo']]
csvinfo = [] 
releaseinfo = []
branchinfo = []

for python_ in version:
    if '-' in python_:
        python = python_.split('-')[0]
    else:
        python = python_
    for i in range(len(config[python_]['pyomo_version'])):
        pyomo = config[python_]['pyomo_version'][i]
        pyutilib = config[python_]['pyutilib_version'][i]
        if pyomo[0] == '-':
            testdir = "%s-%s" % (python_,pyomo[1:])
            csvinfo.append([testdir, python_, pyomo[1:]])
            branchinfo.append([testdir, python_, pyomo[1:]])
        else:
            testdir = "%s-%s" % (python_, pyomo)
            csvinfo.append([testdir, python_, pyomo])
            releaseinfo.append([testdir, python_, pyomo])

        print("")
        print("DIRECTORY: "+testdir)
        print("PYTHON:    "+python)
        print("")
        if os.path.exists(testdir):
            print("  Directory exists.  Skipping installation!")
            continue

        if False and using_modules:
            subprocess.call([sys.executable, '/home/jenkins/bin/pyomo_install', '-p', python, '--venv', testdir, '--venv-only'])
        else:
            subprocess.call(['virtualenv', '-p', python, testdir])
        subprocess.call(['%s/bin/easy_install' % testdir, 'pip'])

        if python_.endswith('cython'):
            subprocess.call(['%s/bin/pip' % testdir, 'install', 'cython'])
        if python == 'pypy' or python == 'python2.7':
            subprocess.call(['%s/bin/pip' % testdir, 'install', 'statistics'])
        subprocess.call(['%s/bin/pip' % testdir, 'install', 'six'])
        if pyomo[0] == '-':
            subprocess.call(['%s/bin/pip' % testdir, 'install', 'git+git://github.com/PyUtilib/pyutilib.git'])
            subprocess.call(['%s/bin/pip' % testdir, 'install', 'git+git://github.com/Pyomo/pyomo.git@%s' % pyomo[1:]])
        else:
            subprocess.call(['%s/bin/pip' % testdir, 'install', 'PyUtilib==%s' % pyutilib])
            subprocess.call(['%s/bin/pip' % testdir, 'install', 'Pyomo==%s' % pyomo])


#
# Save info in the install.csv file
#
with open('install.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in csvinfo:
        writer.writerow(row)

with open('releases.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in releaseinfo:
        writer.writerow(row)

with open('branches.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in branchinfo:
        writer.writerow(row)

