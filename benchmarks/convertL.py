import convert
import sys

#
# We baseline releases with more trials
#
if sys.argv[3][0] in '0123456789':
    R = 10
else:
    R = 1

convert.run(R, sys.argv[1], sys.argv[2], sys.argv[3], True, verbose=True, debug=False)
