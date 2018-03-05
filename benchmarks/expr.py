from pyomo.environ import *
import platform
import pyomo.version
import datetime
import timeit
import signal
import os
import sys
import csv
import statistics

try:
    import pyomo.core.expr.current as EXPR
    from pyomo.repn import generate_standard_repn
    expr_dev = True
except:
    from pyomo.repn import generate_ampl_repn
    expr_dev = False


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


model = ConcreteModel()


# CONST:    sum_i p_i * q_i
# SIMPLE:   sum_i x_i
# WEIGHTED: sum_i 2 * x_i
# PARAM:    sum_i p_i * x_i
# MUTABLE:  sum_i q_i * x_i
# NESTED:   sum_i q_i * (1 + x_i)
# BILINEAR: sum_i y_i * x_i
# NONL:     sum_i q_i * sin(x_i)

def const1():
    return sum(model.p[i]*model.q[i] for i in model.A)

def const2():
    return summation(model.p, model.q, index=model.A)

def const3():
    expr=0
    for i in model.A:
        expr += model.p[i] * model.q[i]
    return expr

def const4():
    expr=0
    for i in model.A:
        expr = expr + model.p[i] * model.q[i]
    return expr

def const5():
    expr=0
    for i in model.A:
        expr = model.p[i] * model.q[i] + expr
    return expr

def const6():
    return Sum(model.p[i]*model.q[i] for i in model.A)

def const7():
    with EXPR.linear_expression as expr:
        expr=sum((model.p[i]*model.q[i] for i in model.A), expr)
    return expr

def const8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.p[i]*model.q[i]
    return expr

def const9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.p[i]*model.q[i]
    return expr

def const10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.p[i]*model.q[i] + expr
    return expr



def simple1():
    return sum(model.x[i] for i in model.A)

def simple2():
    return summation(model.x)

def simple3():
    expr=0
    for i in model.A:
        expr += model.x[i]
    return expr

def simple4():
    expr=0
    for i in model.A:
        expr = expr + model.x[i]
    return expr

def simple5():
    expr=0
    for i in model.A:
        expr = model.x[i] + expr
    return expr

def simple6():
    return Sum(model.x[i] for i in model.A)

def simple7():
    with EXPR.linear_expression as expr:
        expr=sum((model.x[i] for i in model.A), expr)
    return expr

def simple8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.x[i]
    return expr

def simple9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.x[i]
    return expr

def simple10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.x[i] + expr
    return expr



def weighted1():
    return sum(2*model.x[i] for i in model.A)

#def weighted2():
#    return summation(model.p, model.x)

def weighted3():
    expr=0
    for i in model.A:
        expr += 2 * model.x[i]
    return expr

def weighted4():
    expr=0
    for i in model.A:
        expr = expr + 2 * model.x[i]
    return expr

def weighted5():
    expr=0
    for i in model.A:
        expr = 2 * model.x[i] + expr
    return expr

def weighted6():
    return Sum(2*model.x[i] for i in model.A)

def weighted7():
    with EXPR.linear_expression as expr:
        expr=sum((2*model.x[i] for i in model.A), expr)
    return expr

def weighted8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += 2*model.x[i]
    return expr

def weighted9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + 2*model.x[i]
    return expr

def weighted10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = 2*model.x[i] + expr
    return expr



def param1():
    return sum(model.p[i]*model.x[i] for i in model.A)

def param2():
    return summation(model.p, model.x)

def param3():
    expr=0
    for i in model.A:
        expr += model.p[i] * model.x[i]
    return expr

def param4():
    expr=0
    for i in model.A:
        expr = expr + model.p[i] * model.x[i]
    return expr

def param5():
    expr=0
    for i in model.A:
        expr = model.p[i] * model.x[i] + expr
    return expr

def param6():
    return Sum(model.p[i]*model.x[i] for i in model.A)

def param7():
    with EXPR.linear_expression as expr:
        expr=sum((model.p[i]*model.x[i] for i in model.A), expr)
    return expr

def param8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.p[i]*model.x[i]
    return expr

def param9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.p[i]*model.x[i]
    return expr

def param10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.p[i]*model.x[i] + expr
    return expr



def mutable1():
    return sum(model.q[i]*model.x[i] for i in model.A)

def mutable2():
    return summation(model.q, model.x)

def mutable3():
    expr=0
    for i in model.A:
        expr += model.q[i] * model.x[i]
    return expr

def mutable4():
    expr=0
    for i in model.A:
        expr = expr + model.q[i] * model.x[i]
    return expr

def mutable5():
    expr=0
    for i in model.A:
        expr = model.q[i] * model.x[i] + expr
    return expr

def mutable6():
    return Sum(model.q[i]*model.x[i] for i in model.A)

def mutable7():
    with EXPR.linear_expression as expr:
        expr=sum((model.q[i]*model.x[i] for i in model.A), expr)
    return expr

def mutable8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.q[i]*model.x[i]
    return expr

def mutable9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.q[i]*model.x[i]
    return expr

def mutable10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.q[i]*model.x[i] + expr
    return expr



def nested1():
    return sum(model.q[i]*(1+model.x[i]) for i in model.A)

#def nested2():
#    return summation(model.q, model.x)

def nested3():
    expr=0
    for i in model.A:
        expr += model.q[i] * (1+model.x[i])
    return expr

def nested4():
    expr=0
    for i in model.A:
        expr = expr + model.q[i] * (1+model.x[i])
    return expr

def nested5():
    expr=0
    for i in model.A:
        expr = model.q[i] * (1+model.x[i]) + expr
    return expr

def nested6():
    return Sum(model.q[i]*(1+model.x[i]) for i in model.A)

def nested7():
    with EXPR.linear_expression as expr:
        expr=sum((model.q[i]*(1+model.x[i]) for i in model.A), expr)
    return expr

def nested8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.q[i]*(1+model.x[i])
    return expr

def nested9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.q[i]*(1+model.x[i])
    return expr

def nested9a():
    with EXPR.linear_expression as expr:
        for i in model.A:
            tmp = model.q[i]*(1+model.x[i])
            expr = expr + tmp
    return expr

def nested10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.q[i]*(1+model.x[i]) + expr
    return expr



def bilinear1():
    return sum(model.y[i]*model.x[i] for i in model.A)

def bilinear2():
    return summation(model.y, model.x)

def bilinear3():
    expr=0
    for i in model.A:
        expr += model.y[i] * model.x[i]
    return expr

def bilinear4():
    expr=0
    for i in model.A:
        expr = expr + model.y[i] * model.x[i]
    return expr

def bilinear5():
    expr=0
    for i in model.A:
        expr = model.y[i] * model.x[i] + expr
    return expr

def bilinear6():
    return Sum(model.y[i]*model.x[i] for i in model.A)

def bilinear7():
    with EXPR.linear_expression as expr:
        expr=sum((model.y[i]*model.x[i] for i in model.A), expr)
    return expr

def bilinear8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.y[i]*model.x[i]
    return expr

def bilinear9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.y[i]*model.x[i]
    return expr

def bilinear10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.y[i]*model.x[i] + expr
    return expr



def nonl1():
    return sum(model.q[i]*sin(model.x[i]) for i in model.A)

#def nonl2():
#    return summation(model.q, model.x)

def nonl3():
    expr=0
    for i in model.A:
        expr += model.q[i] * sin(model.x[i])
    return expr

def nonl4():
    expr=0
    for i in model.A:
        expr = expr + model.q[i] * sin(model.x[i])
    return expr

def nonl5():
    expr=0
    for i in model.A:
        expr = model.q[i] * sin(model.x[i]) + expr
    return expr

def nonl6():
    return Sum(model.q[i]*sin(model.x[i]) for i in model.A)

def nonl7():
    with EXPR.linear_expression as expr:
        expr=sum((model.q[i]*sin(model.x[i]) for i in model.A), expr)
    return expr

def nonl8():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr += model.q[i]*sin(model.x[i])
    return expr

def nonl9():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = expr + model.q[i]*sin(model.x[i])
    return expr

def nonl10():
    with EXPR.linear_expression as expr:
        for i in model.A:
            expr = model.q[i]*sin(model.x[i]) + expr
    return expr




if expr_dev:
    def trial(func, repn=False):
        try:
            with timeout(10):
                expr = func()
                if repn:
                    generate_standard_repn(expr, quadratic=False)
        except:
            pass
else:
    def trial(func, repn=False):
        try:
            with timeout(10):
                expr = func()
                if repn:
                    generate_ampl_repn(expr)
        except TimeoutError:
            pass
        except:
            raise


def run(N, R, rfile, python, release, skip=False):

    model.A = RangeSet(N)
    model.p = Param(model.A, default=2)
    model.q = Param(model.A, default=2, mutable=True)
    model.x = Var(model.A, initialize=2)
    model.y = Var(model.A, initialize=3)

    results = {}
    data = []
    if os.path.exists(rfile):
        print("  Loading results from file '%s'" % rfile)
        with open(rfile, 'r') as f:
            reader = csv.reader(f)
            i = 0
            for row in reader:
                if row[0] == python and row[1] == release:
                    if not (row[0],row[1],row[2]) in results:
                        results[row[0],row[1],row[2]] = []
                    results[row[0],row[1],row[2]].append(row)
                else:
                    data.append(row)
                i += 1
        #print(len(data))
        #print(len(results))

    if skip:
        ids = [1,2,3,6]
    else:
        ids = list(range(1,7))

    for name in ['const', 'simple', 'weighted', 'param', 'mutable', 'nested', 'bilinear', 'nonl']:
        sys.stdout.write(name+" ")
        for i in ids:
            timer = timeit.Timer('trial(%s%d, True)' % (name,i), 'from expr import trial, %s%d' % (name,i))
            exp = name+"_%d" % i
            values = []
            try:
                num = R - len(results.get((python, release, exp), []))
                if num > 0:
                    sys.stdout.write("\nTiming %d trials\n" % num)
                    sys.stdout.flush() 
                    values = timer.repeat(num, number=1)
                    sys.stdout.write("Done\n")
                    sys.stdout.write("\n")
                    sys.stdout.flush() 
            except:
                pass
            for row in results.get((python, release, exp), []):
                data.append(row)
            for value in values:
                data.append( [python, release, exp, value, None, str(datetime.date.today()), platform.node()] )
            sys.stdout.write(".")
            sys.stdout.flush()
        sys.stdout.write("\n")

    with open(rfile, 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')
        for line in data:
            #print(line)
            writer.writerow(line)

#if __name__ == '__main__':
#    #N = 100000
#    N = 10
#    R = 6
#    run(N, R, 'expr10_results.csv', 'dummy')

