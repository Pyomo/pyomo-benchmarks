"""
MultirankCP module for change-point detection.
Main function :
multiRankChangePointDetect
"""
import inspect, os
from numpy import loadtxt,asarray,exp
from scipy.optimize.zeros import brentq
from scipy.special import gamma,jv

from . multirank import *


## WARNING : only works for up to 100 dimensions !
currdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
zerosBessel = loadtxt(os.path.join(currdir, "besselZ.txt")) # zerosBessel[i,j] = j+1 th zero of J(i+1-2/2)
nD,nN = zerosBessel.shape
## NU = arange(1.,nD+1)/2-1  # h-2 /2


def pValSqBB(h,alpha):
    """ Calc cdf for max of h squared brownian bridges test statistic
    parameters
    ----------
    h : number of brownian bridges
    a : array or scalar, of test levels

    returns
    -------
    threshold
    """
    
    nIter = 50
    alpha = asarray(alpha)

    if alpha.ndim == 0:
        a_rep = alpha[newaxis]
    else:
        a_rep = alpha[:,newaxis].repeat(nIter,axis=1)


    coef = 4./(gamma(h/2.)*(2**(h/2.))*(alpha**h))
    denom = jv(h/2.,zerosBessel[h-1,:nIter])**2

    numerateur = zerosBessel[h-1,:nIter]**(h-2)*exp(-(zerosBessel[h-1,:nIter]**2)/(2.*a_rep**2))

    res = (numerateur/denom).sum(axis=alpha.ndim)

    return coef*res


def findThresholdSqBB(h,alpha):
    """Calc threshold at level alpha for distrib max of d independant squared brownian bridges
    """

    alpha = asarray(alpha)

    if alpha.ndim == 0:
        alpha = alpha[newaxis]

    resArray = empty(alpha.shape)
    for ind,alp in enumerate(alpha):
        def f(x): return pValSqBB(h,x)-alp
        # brentq is a routine using Brent method to find
        # the zero of a function f
        # brentq(f,minGuess,maxGuess)
        resArray[ind] = brentq(f,.2,6)
    return resArray
        

def pValStatCh(h,t):
    return 1-pValSqBB(h,sqrt(t))


    
def multiRankChangePointDetect(X,C,invtol=None):
    '''Rank-based multivariate change-point detection
    Parameters
    ----------
    X : numpy array of data. dimension x sample size
    C : missing values array. Same dimensions as X. C[i,j]== 1 if X[i,j] is not missing, 0 otherwise

    Returns
    -------
    maxVal : value of the maximum of the statistic on the whole windows
    maxPos : position of the change
    pval : p-value of the change-point detection test
    nLib : number of dimensions taken into account (in case covariance matrix is not invertible and pseudo inverse is used)
    stats : value of the statistics for every position.    
    '''
    if X.ndim == 2:
        K,P = X.shape
    else:
        P = X.shape
        K = 1

    nLib = -1
    
    Xsup = X.astype(float)
    Xinf = Xsup.copy()
    censored = (C==0)
    Xinf[censored]=-inf

    cdf,cdfComp = createCDFTables(Xsup,Xinf)
    G = cov((cdf-cdfComp)/float(P),bias=1)

    if invtol:
        Sinv,nLib = psinv(G,tol=invtol)
    else:
        Sinv,nLib = psinv(G)


    res = [multirank(X,C,t,pvalout=True,
                            nbSma=cdf,nbGreat=cdfComp,
                            invMatrix=Sinv,nd=nLib) for t in range(P)]
 
    stats,pval = zip(*res)
    stats = array(stats)
    
    maxPos = stats.argmax()
    maxVal = stats[maxPos]

    
    pval = pValStatCh(nLib,maxVal)

    
    return maxVal,maxPos,pval,nLib,stats

    
