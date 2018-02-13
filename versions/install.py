#
# Install different versions of Pyomo on different versions
# of Python.
#
import subprocess
import os
import shutil
import csv


#python = ['pypy', 'python3.6', 'python2.7']
python = ['python3.6']
pyomo_version    = ['.master', '.expr_dev', '5.3', '5.2', '5.1',   '5.0']
pyutilib_version = ['5.6',     '5.6',       '5.6', '5.5', '5.4.1', '5.4.1']

csvinfo = [['directory', 'python', 'pyomo']]

for p in python:
    for i in range(len(pyomo_version)):
        pyomo = pyomo_version[i]
        pyutilib = pyutilib_version[i]
        if pyomo[0] == '.':
            testdir = "%s_%s" % (p,pyomo[1:])
            csvinfo.append([testdir, p, pyomo[1:]])
        else:
            testdir = "%s_%s" % (p,pyomo)
            csvinfo.append([testdir, p, pyomo])

        print("")
        print("DIRECTORY: "+testdir)
        print("")
        if os.path.exists(testdir):
            print("  Directory exists.  Skipping installation!")
            continue
            #shutil.rmtree(testdir)

        subprocess.run(['virtualenv', '-p', p, testdir])
        if p.startswith('python'):
            subprocess.run(['%s/bin/pip' % testdir, 'install', 'cython'])
        if pyomo[0] == '.':
            subprocess.run(['%s/bin/pip' % testdir, 'install', 'PyUtilib'])
            subprocess.run(['%s/bin/pip' % testdir, 'install', 'git+git://github.com/Pyomo/pyomo.git@%s' % pyomo[1:]])
        else:
            subprocess.run(['%s/bin/pip' % testdir, 'install', 'PyUtilib==%s' % pyutilib])
            subprocess.run(['%s/bin/pip' % testdir, 'install', 'Pyomo==%s' % pyomo])


#
# Save info in the install.csv file
#
with open('install.csv', 'w') as csvfile:
    writer = csv.writer(csvfile)
    for row in csvinfo:
        writer.writerow(row)


