"""
Three ways of computing the Hellinger distance between two discrete
probability distributions using NumPy and SciPy.

source: https://gist.github.com/larsmans/3116927

Extra note:
To anyone that finds this gist at a later date and you're getting 
the exception ValueError: array must not contain infs or NaNs.

Make sure that the distributions given to these functions only
contain positive values. Otherwise, sqrt is going to cause you pain.
Throw them through np.absolute() first if you need to.
"""
 
import numpy as np
from scipy.linalg import norm
from scipy.spatial.distance import euclidean

_SQRT2 = np.sqrt(2)     # sqrt(2) with default precision np.float64

def hellinger1(p, q):
    return norm(np.sqrt(p) - np.sqrt(q)) / _SQRT2

def hellinger2(p, q):
    return euclidean(np.sqrt(p), np.sqrt(q)) / _SQRT2

def hellinger3(p, q):
    return np.sqrt(np.sum((np.sqrt(p) - np.sqrt(q)) ** 2)) / _SQRT2
