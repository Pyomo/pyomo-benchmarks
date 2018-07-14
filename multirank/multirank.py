#!/usr/bin/python2.5 -u
#from numpy import *
"""multirank module for testing homogeneity
See multirank.multirank
"""
import numpy
from numpy import sqrt, array, dot, newaxis, nonzero, empty, cov, inf
from numpy.linalg import svd
from scipy.stats import chi2


def createCDFTables(X,Y):
    n,m = X.shape
    nY,mY = Y.shape
    
    Xs = X.copy()
    Ys = Y.copy()
    Xs.sort(axis=1)
    Ys.sort(axis=1)
    
    cdf = empty(X.shape) # number of smaller elements
    cdfComp = empty(X.shape) # nb of greater elements

    for ind,dim in enumerate(X):
        cdf[ind] = Xs[ind].searchsorted(Y[ind],side='right')
        cdfComp[ind] = m-Ys[ind].searchsorted(X[ind])

    return cdf,cdfComp
        

    


def psinv(M,tol=1.0000000000000001e-15):
    """Compute the (Moore-Penrose) pseudo-inverse of a matrix.

    Calculate pseudo-inverse of a matrix using its singular-value
    decomposition, and including large singular values.
    
    Difference with the numpy-built-in pinv function is that psinv also returns
    the number of eigen values that were kept.

    Parameters
    ----------
    M : 2-D array (matrix) to be inverted

    tol : float ; cutoff for 'small'singular values.

    Returns
    -------
    Minv : pseudo inverse
    dim  : number of singular values that were kept.
    """
    if M.ndim == 0:
        M=M[newaxis,newaxis]
        
    U,s,Vt = svd(M)
    
    threshold = max(s)*tol

    m = U.shape[0]
    n = Vt.shape[1]

    for i in range(min(n,m)):
        if s[i] > threshold:
            s[i] = 1./s[i]
        else:
            s[i] = 0.;

    
    Minv = dot(Vt.T, numpy.multiply(s[:, newaxis],U.T))
    dim = nonzero(s)[0].size

    return Minv,dim

def multirank(X,C,tau,pvalout=True,
                     invMatrix=None,invtol=None,nd=None,nbSma=None,nbGreat=None,bonf=False):
    """
    Parameters
    ----------
    X: data array
    C: censorship array (1= non censored / 0= censored) | use ones(X.shape) if no censorship
    tau: index of supposed change
    pvalout: boolean ; if True, only returns statistic and pval

    Returns
    -------
    stat,pval where
    stat : value of the statistic
    pval : associated p-value

    if pvalout=False:
    Tn_array,G,stat where :
    
    Tn_array = marginal statistic
    G : covariance matrix
    stat : multirank statistic

    
    """
    if X.ndim == 2:
        K,P = X.shape
    else:
        P = X.shape
        K = 1

    Xsup = X.astype(float)
    Xinf = Xsup.copy()
    censored = (C==0)
    ## missing data case ;
    Xinf[censored]=-inf



    T_n = []

    t0 = float(tau)/P

    if nbSma == None or nbGreat == None:
        nbSma,nbGreat = createCDFTables(Xsup,Xinf)

    
    for k in xrange(K):

        t = 0

        cdf = nbSma[k]
        cdfComp = nbGreat[k]

        t = (cdf[:tau]-cdfComp[:tau]).sum()

        T_n.append(t/sqrt(P)/P)
             
       

    ### construit la matrice de correlation

    if invMatrix == None:
  
        G = t0*(1-t0)*cov((nbSma-nbGreat)/float(P),bias=1)
        


        if G.ndim < 2:
            G = array([[G]])

        if invtol:
            Sinv,nLib = psinv(G,tol=invtol)
        else:
            Sinv,nLib = psinv(G)

    else:  # cas change detection
   
        Sinv = invMatrix#/3.
        nLib = nd
        G=None
        
            
    ### /build Sigma
            

    Tn_array = array(T_n)

    stat = dot(dot(Tn_array,Sinv),Tn_array.T)

    pval = chi2(nLib).sf(stat)

    #print "Pval, ndim "+str(pval)+" "+str(nLib)
    if bonf:
        return stat,pval,abs(Tn_array).max()
    if pvalout:
        return stat,pval
    else:
        return Tn_array,G,stat


