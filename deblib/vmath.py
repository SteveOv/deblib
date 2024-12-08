"""
Simple numpy math functions extended with support for uncertainties/ufloats.
Not a fully general purpose implementation, but rather supporting the needs of
this package. What it does do, which uncertainties.umath does not, is to apply
vectorised operations on input values made up of lists or numpy ndarrays. 
"""
from typing import Iterable, Callable, Any
from itertools import chain
import numpy as np
from uncertainties import unumpy, UFloat, ufloat

def degrees(x):
    """ Convert angles from radians to degrees """
    return __call_simple_func_with_unc(x, np.degrees, lambda _: np.degrees(1))

def radians(x):
    """ Convert angles from degrees to radians """
    return __call_simple_func_with_unc(x, np.radians, lambda _: np.radians(1))

def sin(x):
    """ Calculate the sin value of x [rad] """
    return __call_simple_func_with_unc(x, np.sin, np.cos)

def cos(x):
    """ Calculate the cos value of x [rad] """
    return __call_simple_func_with_unc(x, np.cos, np.sin)

def tan(x):
    """ Calculate the tan value of x [rad] """
    return __call_simple_func_with_unc(x, np.tan, lambda n: 1+np.tan(n)**2)

def arcsin(x):
    """ Calculate the inverse sin value of x """
    return __call_simple_func_with_unc(x, np.arcsin, lambda n: 1/np.sqrt(1-n**2))

def arccos(x):
    """ Calculate the inverse cos value of x """
    return __call_simple_func_with_unc(x, np.arccos, lambda n: -1/np.sqrt(1-n**2))

def arctan(x):
    """ Calculate the inverse tan value of x """
    return __call_simple_func_with_unc(x, np.arctan, lambda n: 1/(1+n**2))

def exp(x):
    """ Calculate the exponential value of x """
    return __call_simple_func_with_unc(x, np.exp, np.exp)

def log10(x):
    """ Calculate the base 10 logarithm value of x """
    return __call_simple_func_with_unc(x, np.log10, lambda n: 1/n/np.log(10))


def __call_simple_func_with_unc(x, f: Callable[[Any], Any], df_by_dx: Callable[[Any], Any]):
    """
    Perform the requested simple function (single argument) on x and propagate
    any uncertainties with the supplied derivative of the function, as;
        f(x +/- Δx) = f(x) +/- f'(x)*Δx

    4 main scenarios;
    - x is primitive (float, int, ...): the result is from numpy func, with no uncertainty
    - x is list or array, all primitive: the result is from numpy func, with no uncertainties
    - x is UFloat: the result is a UFloat with nom from numpy func and unc from the derivative
    - x is list or array, some or all UFloats: result is array of all UFloats
        - nominals will be from numpy func and uncertainty from the derivative
        - input uncertainties for non-UFloats will be treated as zero

    :x: the input value - single or Iterable of primative numeric or UFloat
    :func: the numpy function to apply to x - must support x as an Iterable
    :df_by_dx: the derivative of func - must support x as an Iterable (ie: operators & numpy funcs)
    :returns: the result as described
    """
    if isinstance(x, UFloat):
        return ufloat(f(x.n), np.abs(df_by_dx(x.n) * x.s))

    if isinstance(x, Iterable):
        if (isinstance(x, np.ndarray) and x.dtype == UFloat.dtype) \
                or next((True for i in chain(x) if isinstance(i, UFloat)), False):
            noms = unumpy.nominal_values(x)
            stds = unumpy.std_devs(x)
            return unumpy.uarray(f(noms), np.abs(df_by_dx(noms) * stds))

    return f(x)
