import convert
import sys

#
# We baseline releases with more trials
#
if len(sys.argv) == 4 and sys.argv[3][0] in '0123456789':
    R = 10
else:
    R = 10

if len(sys.argv) == 2:
    import os
    import platform
    if os.path.exists(sys.argv[1]):
        os.remove(sys.argv[1])
    convert.run(R, sys.argv[1], "%s %s" % (platform.python_implementation(), platform.python_version()), 'trials', True, verbose=True, debug=False)
else:
    convert.run(R, sys.argv[1], sys.argv[2], sys.argv[3], True, verbose=True, debug=False)
