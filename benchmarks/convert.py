from pyomo.environ import *
import timeit
import signal
import os
import os.path
import sys
import csv
import statistics
import pyutilib.subprocess
from functools import partial
import re
import platform
import datetime

TODAY = str(datetime.datetime.utcnow())
TIMEOUT=60

implementation = platform.python_implementation()
exdir = os.path.abspath(os.getcwd()+'/../models')
auxdir = os.path.abspath(os.getcwd()+'/../../pyomo-nonpublic-models')

#
# Logic to execute test problems
#
def pmedian(format_, name, num, verbose):
    return run_pyomo(format_, "%s/pmedian/pmedian1.py %s/pmedian/pmedian.test%d.dat" % (exdir, exdir, num), verbose)

def pmedian_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/pmedian/pmedian2.py %s/pmedian/pmedian.test%d.dat" % (exdir, exdir, num), verbose)

def bilinear(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/bilinear1_%d.py" % (exdir, num), verbose)

def bilinear_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/bilinear2_%d.py" % (exdir, num), verbose)

def diag(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/diag1_%d.py" % (exdir, num), verbose)

def diag_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/diag2_%d.py" % (exdir, num), verbose)

def stochpdegas1(format_, name, num, verbose):
    return run_script(format_, "run_stochpdegas1_automatic.py", verbose, cwd='%s/dae/' % exdir)

def jump_clnlbeam(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/clnlbeam.py %s/jump/clnlbeam-%d.dat" % (exdir, exdir, num), verbose)

def jump_facility(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/facility%d.py" % (exdir,num), verbose)

def jump_facility_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/facility%d_quick.py" % (exdir,num), verbose)

def jump_lqcp(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/lqcp%d.py" % (exdir,num), verbose)

def jump_lqcp_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/lqcp%d_quick.py" % (exdir,num), verbose)

def jump_opf(format_, name, num, verbose):
    return run_pyomo(format_, "opf_%dbus.py" % num, verbose, cwd='%s/jump/' % exdir)

def jump_opf_quick(format_, name, num, verbose):
    return run_pyomo(format_, "opf_%dbus_quick.py" % num, verbose, cwd='%s/jump/' % exdir)

def dcopf1(format_, name, num, verbose):
    return run_script(format_, "perf_test_dcopf_case2383wp.py", verbose, cwd='%s/dcopf/' % auxdir)

def uc1(format_, name, num, verbose):
    return run_pyomo(format_, "%s/uc/ReferenceModel.py %s/uc/2014-09-01-expected.dat" % (auxdir, auxdir), verbose)

#
# This can be set to a string for a branch name that is 
# used to filter problems that require a specific branch to run
#
dev_branch = None
#
# Configuration of test problems
#
problems = [
    #-------------------------------------------------------------------
    #FUNCION                NUM         LINEAR      LARGE       BRANCH
    #-------------------------------------------------------------------
    (pmedian,               4,          True,       False,      False),
    (pmedian_quick,         4,          True,       False,      False),
    (pmedian,               8,          True,       True,       False),
    (pmedian_quick,         8,          True,       True,       False),
    (bilinear,              100,        False,      False,      False),
    (bilinear_quick,        100,        False,      False,      False),
    (bilinear,              100000,     False,      True,       False),
    (bilinear_quick,        100000,     False,      True,       False),
    (diag,                  100,        True,       False,      False),
    (diag_quick,            100,        True,       False,      False),
    (diag,                  100000,     True,       True,       False),
    (diag_quick,            100000,     True,       True,       False),
    (jump_opf,              662,        False,      False,      False),
    (jump_opf_quick,        662,        False,      False,      False),
    (jump_opf,              6620,       False,      True,       False),    #66200   VERY LARGE
    (jump_opf_quick,        6620,       False,      True,       False),     #66200
    (jump_clnlbeam,         5000,       False,      False,      False),
    (jump_clnlbeam,         50000,      False,      True,       False),    #500000
    (jump_lqcp,             500,        False,      True,       False),
    (jump_lqcp_quick,       500,        False,      True,       False),
    #(jump_lqcp,             2000,       False,      True,       False),    VERY LARGE
    #(jump_lqcp_quick,       2000,       False,      True,       False),
    (jump_facility,         25,         True,       True,       False),
    (jump_facility_quick,   25,         True,       True,       False),
    #(jump_facility,         75,         True,       True,       False),    VERY LARGE
    #(jump_facility_quick,   75,         True,       True,       False),
    (stochpdegas1,          0,          False,      None,       False),
]
if os.path.exists(auxdir):
    problems.append( (dcopf1,           0, True,  None, False) )
    problems.append( (uc1,              0, True,  True, False) )




class TimeoutError(Exception):
    pass

class Xtimeout:
    def __init__(self, seconds=10, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def cat(fname):
    if not os.path.exists(fname):
        return
    with open(fname, 'r') as INPUT:
        for line in INPUT:
            sys.stdout.write(line)


#
# Execute a function 'n' times, collecting performance statistics and
# averaging them
#
def measure(f, n=25):
    """measure average execution time over n trials"""
    _data = []
    for i in range(n):
        _data.append(f())
        sys.stdout.write('.')
        sys.stdout.flush()
    sys.stdout.write('\n')
    return _data


#
# Evaluate Pyomo output
#
def evaluate(logfile, seconds, verbose):
    with open(logfile, 'r') as OUTPUT:
        if verbose:
            sys.stdout.write("*" * 50 + "\n")

        for line in OUTPUT:
            if verbose:
                sys.stdout.write(line)
            tokens = re.split('[ \t]+', line.strip())
            if len(tokens) < 2:
                pass
            elif tokens[1] == 'seconds' and tokens[2] == 'required':
                if tokens[3:5] == ['to', 'construct']:
                    seconds['construct'] = float(tokens[0])
                elif tokens[3:6] == ['to', 'write', 'file']:
                    seconds['write_problem'] = float(tokens[0])
                elif tokens[3:6] == ['to', 'read', 'logfile']:
                    seconds['read_logfile'] = float(tokens[0])
                elif tokens[3:6] == ['to', 'read', 'solution']:
                    seconds['read_solution'] = float(tokens[0])
                elif tokens[3:5] == ['for', 'solver']:
                    seconds['solver'] = float(tokens[0])
                elif tokens[3:5] == ['for', 'presolve']:
                    seconds['presolve'] = float(tokens[0])
                elif tokens[3:5] == ['for', 'postsolve']:
                    seconds['postsolve'] = float(tokens[0])
                elif tokens[3:6] == ['for', 'problem', 'transformations']:
                    seconds['transformations'] = float(tokens[0])

        if verbose:
            sys.stdout.write("*" * 50 + "\n")
    return seconds


#
# Convert a test problem
#
def run_pyomo(format_, problem, verbose, cwd=None):

    if verbose:
        options = ""  # TODO
    else:
        options = ""

    def f():
        cmd = sys.exec_prefix + '/bin/pyomo convert --report-timing --output=file.%s %s  %s' % (format_, options, problem)
        _cwd = os.getcwd()
        if not cwd is None:
            os.chdir(cwd)
        if verbose:
            print("Command: %s" % cmd)
        res = pyutilib.subprocess.run(cmd, outfile='pyomo.out', verbose=verbose, timelimit=TIMEOUT)
        if res[0] != 0:
            print("Aborting performance testing because an error was generated!: %s" % str(res))
            print("")
            print("Pyomo Logfile: ")
            cat('pyomo.out')
            print("")
            os.chdir(_cwd)
            return {}

        seconds = {}
        eval_ = evaluate('pyomo.out', seconds, verbose)
        os.chdir(_cwd)
        return eval_

    return f


#
# Convert a test problem
#
def run_script(format_, problem, verbose, cwd=None):

    if verbose:
        options = ""  # TODO
    else:
        options = ""

    def f():
        cmd = sys.exec_prefix + '/bin/python %s pyomo.%s' % (problem, format_)
        if verbose:
            print("Command: %s" % cmd)
        _cwd = os.getcwd()
        os.chdir(cwd)
        res = pyutilib.subprocess.run(cmd, outfile='pyomo.out', verbose=verbose, timelimit=TIMEOUT)
        os.chdir(_cwd)
        if res[0] != 0:
            print("Aborting performance testing because an error was generated!: %s" % str(res))
            print("")
            print("Pyomo Logfile: ")
            cat('pyomo.out')
            print("")
            return {}

        seconds = {}
        return evaluate(cwd+'/pyomo.out', seconds, verbose)

    return f


def run(R, rfile, python, release, large, verbose=False, debug=True, timeout=None):

    global TIMEOUT
    if timeout is not None:
        TIMEOUT=timeout
    elif large:
        TIMEOUT=600
    else:
        TIMEOUT=60

    global problems
    if debug:
        problems = [(pmedian, 4, True, None, False), (diag, 100, True, None, False)]

    mykeys = set()
    results = {}
    data = []
    if os.path.exists(rfile):
        print("  Loading results from file '%s'" % rfile)
        with open(rfile, 'r') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if row[1] == python and row[2] == release:
                    mykeys.add(row[5])
                    ndx = tuple(row[1:6])
                    if not ndx in results:
                        results[ndx] = []
                    results[ndx].append(row)
                else:
                    data.append(row)
                i += 1

    for fn, num, linear, large_, dev_ in problems:
        #
        # Skip problems that either don't match the size
        # specification, or which cannot be run with this
        # release.
        #
        if dev_ and release != dev_branch:
            continue
        if not (large_ is None or large == large_):
            continue

        name = fn.__name__
        exp = name+"_%d" % num
        sys.stdout.write(name+" ")
        if linear:
            #formats = ['lp', 'nl', 'bar', 'gms']
            formats = ['lp', 'nl']
        else:
            #formats = ['nl', 'bar', 'gms']
            formats = ['nl']
        for format_ in formats:
            f = partial(fn, format_, name, num, verbose)()
            values = []
            print(python, release, exp, format_)
            try:
                R_ = R - len(results.get((python, release, exp, format_, 'total'), []))
                print("R:      "+str(R))
                print("# done: "+str(R-R_))
                if R_ > 0:
                    values = values = measure(f, n=R_)
            except Exception as e:
                print("EXCEPTION OCCURRED: %s" % str(e))

            for key in mykeys:
                for row in results.get((python, release, exp, format_, key), []):
                    data.append(row)

            if len(values) > 0:
                for val in values:
                    print(val)

                totals = []
                for key in ['construct','write_problem']:
                    vals = [trial.get(key,None) for trial in values]
                    if len(totals) == 0:
                        totals = vals
                    else:
                        for i in range(len(totals)):
                            if vals[i] is None:
                                totals[i] = None
                            if not totals[i] is None:
                                totals[i] += vals[i]
                    for val in vals:
                        data.append( [TODAY, python, release, exp, format_, key, val, None, platform.node()] )
                for val in totals:
                    if not val is None:
                        data.append( [TODAY, python, release, exp, format_, 'total', val, None, platform.node()] )

        sys.stdout.write("\n")

    print("Writing results to file: %s (%d lines)" % (rfile, len(data)))
    with open(rfile, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in data:
            writer.writerow(line)

if __name__ == '__main__':
    run(3, 'foo.csv', 'dummy', 'curr', True, True, False)

