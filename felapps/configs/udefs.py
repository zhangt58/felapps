"""
user-defined functions to process A,
A could be any type of:
    1: 1D scalar
    2: 2D array
    3: list

Potentially be used by 'cornalyzer', i.e. correlation analyzer application.

Created: 2016-07-14 14:59:11 PM CST
"""

import numpy as np

def f_magnify(x):
    """ multipy by 10 folds
    """
    a = 10
    return x * a

def f_shrink(x):
    """ half value
    """
    a = 0.5
    return x * a

def f_cos(x):
    """ return sum of cos(x)
    """
    return np.sum(np.cos(x))
