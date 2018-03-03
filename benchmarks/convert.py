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

implementation = platform.python_implementation()
exdir = os.path.abspath(os.getcwd()+'/../models')
auxdir = os.path.abspath(os.getcwd()+'/../pyomo-models')


class TimeoutError(Exception):
    pass

class timeout:
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


#
# Execute a function 'n' times, collecting performance statistics and
# averaging them
#
def measure(f, n=25):
    """measure average execution time over n trials"""
    data = []
    for i in range(n):
        data.append(f())
        sys.stdout.write('.')
        sys.stdout.flush()
    sys.stdout.write('\n')
    return data


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
            #print(tokens)
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
        res = pyutilib.subprocess.run(cmd, outfile='pyomo.out', verbose=verbose)
        if res[0] != 0:
            print("Aborting performance testing!")
            sys.exit(1)

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
        cmd = sys.exec_prefix + '/bin/lpython %s pyomo.%s' % (problem, format_)
        if verbose:
            print("Command: %s" % cmd)
        _cwd = os.getcwd()
        os.chdir(cwd)
        res = pyutilib.subprocess.run(cmd, outfile='pyomo.out', verbose=verbose)
        os.chdir(_cwd)
        if res[0] != 0:
            print("Aborting performance testing!")
            sys.exit(1)

        seconds = {}
        return evaluate(cwd+'/pyomo.out', seconds, verbose)

    return f


def pmedian1(format_, name, num, verbose):
    return run_pyomo(format_, "%s/pmedian/pmedian1.py %s/pmedian/pmedian.test%d.dat" % (exdir, exdir, num), verbose)

def pmedian2(format_, name, num, verbose):
    return run_pyomo(format_, "%s/pmedian/pmedian2.py %s/pmedian/pmedian.test%d.dat" % (exdir, exdir, num), verbose)

def bilinear1(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/bilinear1_%d.py" % (exdir, num), verbose)

def bilinear2(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/bilinear2_%d.py" % (exdir, num), verbose)

def diag1(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/diag1_%d.py" % (exdir, num), verbose)

def diag2(format_, name, num, verbose):
    return run_pyomo(format_, "%s/misc/diag2_%d.py" % (exdir, num), verbose)

def stochpdegas1(format_, name, num, verbose):
    return run_script(format_, "run_stochpdegas1_automatic.py", verbose, cwd='%s/dae/' % exdir)

def dcopf1(format_, name, num, verbose):
    return run_script(format_, "perf_test_dcopf_case2383wp.py", verbose, cwd='%s/dcopf/' % auxdir)

def uc1(format_, name, num, verbose):
    return run_pyomo(format_, "%s/uc/ReferenceModel.py %s/uc/2014-09-01-expected.dat" % (auxdir, auxdir), verbose)

def jump_clnlbeam(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/clnlbeam.py %s/jump/clnlbeam-%d.dat" % (exdir, exdir, num), verbose)

def jump_facility(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/facility.py" % exdir, verbose)

def jump_facility_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/facility_quick.py" % exdir, verbose)

def jump_lqcp(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/lqcp.py" % exdir, verbose)

def jump_lqcp_quick(format_, name, num, verbose):
    return run_pyomo(format_, "%s/jump/lqcp_quick.py" % exdir, verbose)

def jump_opf(format_, name, num, verbose):
    return run_pyomo(format_, "opf_%dbus.py" % num, verbose, cwd='%s/jump/' % exdir)

def jump_opf_quick(format_, name, num, verbose):
    return run_pyomo(format_, "opf_%dbus_quick.py" % num, verbose, cwd='%s/jump/' % exdir)


def run(R, large, verbose, args):

    if len(args) == 1:
        raise RuntimeError("Missing filename")
    if os.path.exists(args[1]):
        print("  Skipping benchmark generation because file '%s' exists" % args[1])
        sys.exit(0)

    if large:
        problems = [
                (pmedian1,      8, True),
                (pmedian2,      8, True),
                (diag1,         100000, True),
                (diag2,         100000, True),
                (jump_opf,      6620, False),
                (jump_clnlbeam, 50000, False),
                #(jump_opf,      66200, False),
                #(jump_clnlbeam, 500000, False),
                (jump_lqcp,     0, False)
                ]
        if implementation == 'CPython':
            problems.append( (bilinear1,     100000, True) )
            problems.append( (bilinear2,     100000, True) )
    else:
        problems = [
                (pmedian1,      4, True),
                (pmedian2,      4, True),
                (bilinear1,     100, True),
                (bilinear2,     100, True),
                (diag1,         100, True),
                (diag2,         100, True),
                (jump_opf,      662, False),
                (jump_clnlbeam, 5000, False),
                ]
        if implementation == 'CPython':
            problems.append( (bilinear1,     100, True) )
            problems.append( (bilinear2,     100, True) )
    problems.append( (stochpdegas1,     0, False) )
    problems.append( (jump_facility,    0, False) )

    if os.path.exists(auxdir):
        problems.append( (dcopf1,           0, True) )
        problems.append( (uc1,              0, True) )

    # FOR DEBUGGING
    problems = [(pmedian1,      4, True), (diag1,         100, True)]

    data = []

    for fn, num, linear in problems:
        name = fn.__name__
        sys.stdout.write(name+" ")
        if linear:
            formats = ['lp', 'nl']
        else:
            formats = ['nl']
        for format_ in formats:
            f = partial(fn, format_, name, num, verbose)()
            try:
                values = measure(f, n=R)
                totals = []
                for key in values[0]:
                    if key == 'transformations':
                        continue
                    vals = [trial[key] for trial in values]
                    if len(totals) == 0:
                        totals = vals
                    else:
                        for i in range(len(totals)):
                            totals[i] += vals[i]
                    data.append( [name+"_%d" % num, format_, key, R, min(vals), statistics.mean(vals), max(vals), statistics.stdev(vals)] )
                data.append( [name+"_%d" % num, format_, "total", R, min(totals), statistics.mean(totals), max(totals), statistics.stdev(totals)] )
            except:
                data.append( [name+"_%d" % num, format_, key, R, None, None, None, None] )
        sys.stdout.write("\n")

    with open(args[1], 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in data:
            writer.writerow(args[2:] + line)

if __name__ == '__main__':
    R = 3
    run(R, False, True, sys.argv)

