import expr
import sys

N = 100000
R = 10

if len(sys.argv) == 2:
    import os
    import platform
    if os.path.exists(sys.argv[1]):
        os.remove(sys.argv[1])
    expr.run(N, R, sys.argv[1], "%s %s" % (platform.python_implementation(), platform.python_version()), 'trials')
else:
    expr.run(N, R, sys.argv[1], sys.argv[2], sys.argv[3])
