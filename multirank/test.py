import numpy 
from numpy import zeros,sqrt
from multirankCP import multiRankChangePointDetect
from dynkw import autoDynKWRupt, DynMultiKW
from multirank import multirank

print "Example of the change-point detection test:"

X = numpy.random.randn(5,100)

X[:,35:] += 1

maxVal,maxPos,pval,nLib,stats = multiRankChangePointDetect(X,numpy.ones(X.shape))

print "Changepoint at position",
print maxPos,
print "with p-value of ",
print pval


#### Multichange point estimation

print "\nMultiple change-point estimation"

winLength = 500
nDim = 5

varNoise = 0.01

signal = zeros((nDim,winLength))
signal[0,130:270]+=0.2
signal[1,440:]+=0.2
signal[2,0:230]+=0.2
signal[3,230:270]+=0.2
signal[4,130:440]+=0.2

noise = sqrt(varNoise)*numpy.random.randn(nDim,winLength)

Y = signal + noise

numCh,chP = autoDynKWRupt(Y)

stats,chgP = DynMultiKW(Y)

knownNbChg = chgP[4]

print numCh,
print "were found in the signal, segment finishes at positions",

print chP[chP!=0]
print "If you know that the number of change points is 4, the positions are", 
print knownNbChg[knownNbChg!=0]

### Test for homogeneity


X = numpy.random.randn(5,500)


stat,pval = multirank(X,numpy.ones(X.shape),240)
print "\ntest for homogeneity:"
print "test statistic:",
print stat,
print "p-value:",
print pval
