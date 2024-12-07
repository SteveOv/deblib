""" Simple math functions with support for vectorised operation and uncertainties/ufloats. """
from typing import Iterable, Callable, Any
import numpy as np
from uncertainties import umath, unumpy

def degrees(x):
    """ Calculate the degrees value of x [rad] """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.degrees, lambda _: np.degrees(1))
    return umath.degrees(x) # pylint: disable=no-member

def radians(x):
    """ Calculate the radians value of x [degrees] """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.radians, lambda _: np.radians(1))
    return umath.radians(x) # pylint: disable=no-member

def sin(x):
    """ Calculate the sin value of x [rad] """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.sin, np.cos)
    return umath.sin(x) # pylint: disable=no-member

def cos(x):
    """ Calculate the cos value of x [rad] """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.cos, np.sin)
    return umath.cos(x) # pylint: disable=no-member

def tan(x):
    """ Calculate the tan value of x [rad] """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.tan, lambda n: 1+np.tan(n)**2)
    return umath.tan(x) # pylint: disable=no-member

def asin(x):
    """ Calculate the inverse sin value of x """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.arcsin, lambda n: 1/np.sqrt(1-n**2))
    return umath.asin(x) # pylint: disable=no-member

def acos(x):
    """ Calculate the inverse cos value of x """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.arccos, lambda n: -1/np.sqrt(1-n**2))
    return umath.acos(x) # pylint: disable=no-member

def atan(x):
    """ Calculate the inverse tan value of x """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.arctan, lambda n: 1/(1+n**2))
    return umath.atan(x) # pylint: disable=no-member

def exp(x):
    """ Calculate the exponential value of x """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.exp, np.exp)
    return umath.exp(x) # pylint: disable=no-member

def log10(x):
    """ Calculate the base 10 logarithm value of x """
    if isinstance(x, Iterable):
        return __simple_vectorised_func_with_unc(x, np.log10, lambda n: 1/n/np.log(10))
    return umath.log10(x) # pylint: disable=no-member


def __simple_vectorised_func_with_unc(x: Iterable,
                                      func: Callable[[Any], Any],
                                      df_by_dx: Callable[[Any], Any]) -> Iterable:
    """
    Perform the requested simple (single argument) function on the Iterable x
    and propagate any uncertainties with the supplied derivative of the function, as;
        f(x +/- Δx) = f(x) +/- f'(x)*Δx

    :x: the input value in some iterable form - primative numeric or ufloats
    :func: the function to apply to x - must support x as an Iterable (ie: numpy funcs)
    :df_by_dx: the derivative of func - must support x as an Iterable (ie: made up of numpy funcs)
    """
    noms = unumpy.nominal_values(x)
    deltas = unumpy.std_devs(x)
    return unumpy.uarray(func(noms), np.abs(df_by_dx(noms) * deltas))
