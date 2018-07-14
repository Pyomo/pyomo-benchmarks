"""
Multivariate change-point estimation
See functions :
autoDynKWRupt for automatic estimation of the number of change-points
DynMultiKW for displaying solutions for a range of values of the number of change-points

See also DynMultiLinear/autoDynMultiLinear for the linear,
max-likehood-based version (under the Gaussian assumption
and DynKernel/autoDynKernel for a kernel based version.

"""
import numpy
from numpy import searchsorted,empty,zeros,triu,arange,argmax,diag,eye,cov,dot,inf,sqrt,mean,exp,isnan,argmin
from numpy.random import permutation
from numpy.matlib import repmat
from multirankCP import multiRankChangePointDetect
from scipy.stats import chi2
from multirank import createCDFTables

import numpy


"""
Kruskal Wallis test is defined by:
K=12/N/N+1 \sum_i=1^s R_i^2/n_i -3(N+1)
where :
 N is sample size
 n_i size of segment_i
 R_i = R_i1+...+R_in_i
 s is number of segments (s-1 segments boundaries)
"""

def dynprog(matD,Kmax):
   """Marc Lavielle dcpc inspired
   """
   N,N = matD.shape
   I = repmat(-inf,Kmax,N)
   t = zeros((Kmax-1,N),dtype=int)

   I[0] = matD[0]

   for k in range(1,Kmax):
      for L in range(k,N):
         am = argmax(matD[1:L+1,L]+I[k-1,0:L])
         t[k-1,L] = am
         I[k,L] =  (matD[1:L+1,L]+I[k-1,0:L])[am]

   J = I[:,N-1]#-3*(N+1) # with correction TO FIX

   t_est = (N-1)*eye(Kmax,dtype=int)
   # backward recursion

   for K in range(1,Kmax):
      for k in range(K-1,-1,-1):
         t_est[K,k] = t[k,t_est[K,k+1]]

   return J,t_est



# "contrast matrix", ie, for each 1<=n1<=n2<=N, calc

def multiRankMatrix(cdf):
    """ returns an upper triangular array
    """
    nDim,winLength = cdf.shape
    M = zeros((winLength,winLength,nDim),dtype=float)
    N = zeros((winLength,winLength))

    R = zeros((winLength,winLength),dtype=float)
    
    #calc inverse sigma
    invSigma = numpy.linalg.inv(cov(cdf)/(winLength*winLength))
    
    for i in range(winLength):
       Ni = arange(1,winLength+1-i,dtype=float)
       N[i,i:]= Ni
       M[i,i:]=(cdf[:,i:].cumsum(axis=1).T/repmat(Ni,nDim,1).T) - winLength/2.



    for i in range(winLength):
       for j in range(i,winLength):
          R[i,j] = N[i,j]*dot(dot(M[i,j],invSigma),M[i,j])
    return R/(winLength*winLength)


def DynMultiKW(x,Kmax = 20):
   """ Dynamic programming + Multivariate KW
   
   Parameters
   ----------
   x : data, size dimension x sample length
   Kmax : maximum number of change points to be computed, default is Kmax = 20
   
   Returns
   -------
   stats : value of the statistic for number of change from 1 to Kmax
   chgP  : Lower triangular matrix of size Kmax x Kmax, with position of the end of the k segments at line k
   """
   nDim,winLength = x.shape

   cdf,cdfComp = createCDFTables(x,x)

   matD = multiRankMatrix(cdf)

   stats,chgP = dynprog(matD,Kmax)

   return stats,chgP
   


def multiKW(x,listCh):
   """
   Multivariate Kruskal Wallis
   x : data (nDim x winLength)
   chP : collection of changePoints
   Do not include 0 and winLength!
   """


   nDim,winLength = x.shape
   chP = list(listCh)
   
   chP.append(winLength)
   chP.append(0)
   chP.sort()
   
   
   cdf,cdfComp = createCDFTables(x,x)

   invSigma = numpy.linalg.inv(numpy.cov(cdf)/(winLength*winLength))

   H = 0.
   
   for i in range(len(chP)-1):
      deb = chP[i]
      fin = chP[i+1]
      R = (cdf[:,deb:fin].sum(axis=1)/(fin-deb))-winLength/2.

      H += (fin-deb)*dot(dot(R,invSigma),R)

   return H/(winLength*winLength)
   



############################
# kernel related functions #
############################
def grammat(X):
    '''Computes Gram matrix for Gaussian kernel with kernel bandwidth as suggested by the authors
    '''
    scaProd = dot(X.T,X)
    N,N = scaProd.shape
    SqNorm = zeros(N)
    for i in range(N):
        SqNorm[i] = (X[:,i]**2).sum()

    K = zeros(scaProd.shape)
    for i in range(N):
        for j in range(N):
            K[i,j]=SqNorm[i]+SqNorm[j]-2*scaProd[i,j]

    empVar = sqrt(((X.T-mean(X,axis=1))**2).sum(axis=1).mean())

    sig = 1.06 * empVar * N**(1./5)

    #med = median(K[K>1e-9])

    return exp(-K/(2*sig*sig))


def kernelIntraScatterFast(K):
    '''Computes kernel intra scatter matrix.
    Argument : K gram matrix
    '''
    N,N = K.shape
    matD = eye(N)

    Ni = eye(N)

    for i in range(N-1):
        for j in range(i+1,N):
            Ni[i,j] = j-i+1
            matD[i,j]=(matD[i,j-1]+2*K[j,i:j+1].sum()-K[j,j])

    R = Ni-matD/Ni ## Ni-, assuming ones on grammat diagonal
    R[isnan(R)]=0.
    return R


def dynprogPos(matD,Kmax):
   """Marc Lavielle dcpc inspired
   """
   N,N = matD.shape
   I = repmat(inf,Kmax,N)
   t = zeros((Kmax-1,N),dtype=int)

   I[0] = matD[0]

   for k in range(1,Kmax):
      for L in range(k,N):
         am = argmin(matD[1:L+1,L]+I[k-1,0:L])
         t[k-1,L] = am
         I[k,L] =  (matD[1:L+1,L]+I[k-1,0:L])[am]

   J = I[:,N-1]#-3*(N+1) # with correction TO FIX

   t_est = (N-1)*eye(Kmax,dtype=int)
   # backward recursion

   for K in range(1,Kmax):
      for k in range(K-1,-1,-1):
         t_est[K,k] = t[k,t_est[K,k+1]]

   return J,t_est


def DynKernel(X,Kmax):
   """
   Dynamic programming + kernel
   """   
   nDim,winLength = X.shape
   K = grammat(X)
   matD = kernelIntraScatterFast(K)

   stats,chgP = dynprogPos(matD,Kmax)

   return stats,chgP
   
#################
# Linear method #
#################

def matContLinear(X):


   nDim,winLength = X.shape
   Xc = (X.T-X.mean(axis=1)).T
   invSigma = numpy.linalg.inv(cov(X))
   
   R = zeros((winLength,winLength),dtype=float)

   M = zeros((winLength,winLength,nDim),dtype=float)
   N = zeros((winLength,winLength))

   for i in range(winLength):
      Ni = arange(1,winLength+1-i,dtype=float)
      N[i,i:]= Ni
      M[i,i:]=(Xc[:,i:].cumsum(axis=1).T/repmat(Ni,nDim,1).T)

   for i in range(winLength):
      for j in range(i,winLength):
         R[i,j] = N[i,j]*dot(dot(M[i,j],invSigma),M[i,j])

   return R


def DynMultiLinear(X,Kmax):
   """
   Dynamic programming + linear test
   """
   nDim,winLength = X.shape
  
   matD = matContLinear(X)

   stats,chgP = dynprog(matD,Kmax)

   return stats,chgP
      
   

def vostri(x,alpha=.01):
   # Multi Rank + Vostrikova
   nDim,winLength = x.shape
   changePoints = []

   def recurSeg(X,C,deb,fin,alpha):
      
      maxVal,maxPos,pval,nLib,stats = multiRankChangePointDetect(X[:,deb:fin],C[:,deb:fin])
      if pval < alpha:
         changePoints.append(maxPos+deb)
         recurSeg(X,C,deb,deb+maxPos,alpha)
         recurSeg(X,C,deb+maxPos,fin,alpha)

   recurSeg(x,numpy.ones(x.shape),0,winLength,alpha)

   return sorted(changePoints)


def rupturepente(leastPC):
   Y = leastPC
   l = leastPC.size
   x = arange(l)

   aL_ = []
   bL_ = []
   aR_ = []
   bR_ = []

   S = []

   for k in range(1,l-1):
      Yleft = Y[:k+1]
      Xleft = arange(0,k+1)

      aL = (mean(Yleft*Xleft)-mean(Yleft)*mean(Xleft))/(mean(Xleft**2.)-(mean(Xleft))**2.)
      bL = mean(Yleft)-aL*mean(Xleft)

      aL_.append(aL)
      bL_.append(bL)
      

      Yright = Y[k:]
      Xright = arange(k,l)

      aR = (mean(Yright*Xright)-mean(Yright)*mean(Xright))/(mean(Xright**2.)-(mean(Xright))**2.)
      bR = mean(Yright)-aR*mean(Xright)

      aR_.append(aR)
      bR_.append(bR)


      S.append( sum((Yleft-aL*Xleft-bL)**2.)+sum((Yright-aR*Xright-bR)**2.) )

   am = argmin(S)
      
   return am+1 #+1 for k started at 1 !



def autoDynKernel(x,Kmax=20):
    nDim,winLength = x.shape
    stats,chP = DynKernel(x,Kmax)
    numCh = rupturepente(stats)
    return numCh,chP[numCh]
   

def autoDynMultiLinear(x,Kmax=20):
    nDim,winLength = x.shape
    stats,chP = DynMultiLinear(x,Kmax)
    numCh = rupturepente(stats)
    return numCh,chP[numCh]

def autoDynKWRupt(x,Kmax=20):
    '''use Dynamic programming Kruskal-Wallis, and automagically returns number of changes using rupturepente heuristic algorithm
    Parameters
    ----------
    x : numpy array of data (nDim x windowLength)
    Kmax : (optional, default to 20) : number of change point to compute before applying slope heuristic

    Returns
    -------
    numCh : number of change points
    chP : array of the position of the end of the segment boundaries for the values that are different to 0.
    '''
    nDim,winLength = x.shape
    stats,chP = DynMultiKW(x,Kmax)
    
    # test on stats[1] to check for homogeneity
    if stats[1]< chi2(nDim).ppf(0.9999):
        return 0,chP[0]
    else:
        numCh = rupturepente(stats)
        
        return numCh,chP[numCh]
