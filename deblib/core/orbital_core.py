""" Primitive functions for Orbital relations. """
# pylint: disable=no-name-in-module
import sys
from enum import Flag
from typing import Tuple, Union
from math import pi, cos, acos, radians, degrees
from astropy.constants import G

from uncertainties.core import wrap
from uncertainties.umath_core import wraps

class EclipseType(Flag):
    """ Indicates which type of eclipse """
    PRIMARY = 1
    SECONDARY = 2

FOUR_PI_SQUARED = 4*pi**2

def __orbital_period(m1: float, m2: float, a: float) -> float:
    """
    Calculates the orbital period from the two components' masses and the
    orbital semi-major axis. The calculation is based on Kepler's 3rd Law.

    P^2 = (4π^2 *a^3) / G(m1 + m2)

    :m1: the first mass in units of kg
    :m2: the second mass in units of kg
    :a: the semi-major axis length in units of m
    :returns: the orbital period in units of s
    """
    return (FOUR_PI_SQUARED * a**3 / (G.value * (m1 + m2)))**0.5

def __semi_major_axis(m1: float, m2: float, period: float) -> float:
    """
    Calculates the orbital semi-major axis of two orbital components from their
    masses and orbital period. The calculation is based on Kepler's 3rd law.

    a^3 = G(m1+m2)P^2/4π^2

    :m1: the first mass in units of kg
    :m2: the second mass in units of kg
    :period: the components' orbital period in units of s
    :returns: the semi-major axis in units of m
    """
    return (G.value * (m1 + m2) * period**2 / FOUR_PI_SQUARED)**(1/3)

def __impact_parameter(r1: float,
                       inc: float,
                       e: float,
                       esinw: float=None,
                       eclipse: EclipseType=EclipseType.PRIMARY) \
                            -> Union[float, Tuple[float, float]]:
    """
    Calculate the impact parameter of one or both eclipse types. This uses
    the primary star's fractional radius, orbital inclination, eccentricity
    and one of either omega or esinw [e*sin(omega)]. While the function can
    calculate e*sin(omega) from e and omega the function may be quicker if
    you supply it directly (as esinw) if you already have it.

    :r1: fractional radius of the primary star
    :inc: the orbital inclination in degrees or radians (assumes rad if inc < 2pi)
    :e: the orbital eccentricity
    :esinw: the e*sin(omega) Poincare element
    :eclipse: the type of eclipse to calculate for PRIMARY, SECONDARY or BOTH.
    :returns: either the primary or secondary dimensionless impact parameter
    """
    if inc > 2*pi:
        inc = radians(inc)

    # Primary eclipse:      (1/r1) * cos(inc) * (1-e^2 / 1+esinw)
    # Secondary eclipse:    (1/r1) * cos(inc) * (1-e^2 / 1-esinw)
    # Only difference is the final divisor so work the common dividend out
    dividend = (1 / r1) * cos(inc) * (1 - e**2)
    return dividend / (1+esinw if eclipse == EclipseType.PRIMARY else 1-esinw)

def __orbital_inclination(r1: float,
                          b: float,
                          e: float,
                          esinw: float=None,
                          eclipse: EclipseType=EclipseType.PRIMARY)\
                                -> float:
    """
    Calculate the orbital inclination from an impact parameter. This uses
    the primary star's fractional radius, orbital eccentricity and the
    e*sin(omega) Poincare element along with the supplied impact parameter.

    :r1: fractional radius of the primary star
    :b: the chosen impact parameter
    :e: the orbital eccentricity
    :esinw: the e*sin(omega) Poincare element
    :eclipse: the type of eclipse the impact parameter is from; PRIMARY or SECONDARY (not BOTH).
    :returns: The inclination as a Quantity in degrees
    """
    # From primary eclipse/impact param:  i = arccos(bP * r1 * (1+esinw)/(1-e^2))
    # From secodary eclipse/impact param: i = arccos(bS * r1 * (1-esinw)/(1-e^2))
    dividend = 1 + esinw if eclipse == EclipseType.PRIMARY else 1 - esinw
    return degrees(acos(b * r1 * dividend / (1 - e**2)))


# This code takes the primitive functions and gives them ufloat aware wrappers then exposes them
# in the __all__ list so they can be imported/published by the public facing orbital module.
# This is following a similar pattern to that used by the uncertainties package's umath module.
__all__ = []
__this_module__ = sys.modules[__name__]

for (public_name, func, assigned, updated) in [
    ("orbital_period",      __orbital_period,       None, None),
    ("semi_major_axis",     __semi_major_axis,      None, None),
    ("impact_parameter",    __impact_parameter,     None, None),
    ("orbital_inclination", __orbital_inclination,  None, None),
]:
    wrapper = wraps(wrap(func), func, assigned or ('__doc__',), updated or ('__dict__',))
    setattr(__this_module__, public_name, wrapper)
    __all__.append(public_name)
