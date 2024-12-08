""" Utility functions for orbital relations. """
# pylint: disable=no-name-in-module, no-member
from typing import Union
from math import pi

import numpy as np
from uncertainties import UFloat

from .vmath import sin, cos, arccos, arctan, radians, degrees
from .constants import G

FOUR_PI_SQUARED = 4*pi**2

def orbital_period(m1: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                   m2: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                   a: Union[float, UFloat, np.ndarray[Union[float, UFloat]]]) \
                        -> Union[UFloat, np.ndarray[UFloat]]:
    """
    Calculates the orbital period from the two components' masses and the
    orbital semi-major axis. The calculation is based on Kepler's 3rd Law.

    P^2 = (4π^2 *a^3) / G(m1 + m2)

    Because G has an uncertainty, the result will always have an uncertainty

    :m1: the first mass in units of kg
    :m2: the second mass in units of kg
    :a: the semi-major axis length in units of m
    :returns: the orbital period and uncertainty in units of s
    """
    # We're not using any math/umath funcs here so this will "just work" with ndarrays
    return (FOUR_PI_SQUARED * a**3 / (G * (m1 + m2)))**0.5


def semi_major_axis(m1: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                    m2: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                    period: Union[float, UFloat, np.ndarray[Union[float, UFloat]]]) \
                        -> Union[UFloat, np.ndarray[UFloat]]:
    """
    Calculates the orbital semi-major axis of two orbital components from their
    masses and orbital period. The calculation is based on Kepler's 3rd law.

    a^3 = G(m1+m2)P^2/4π^2

    Because G has an uncertainty, the result will always have an uncertainty

    :m1: the first mass in units of kg
    :m2: the second mass in units of kg
    :period: the components' orbital period in units of s
    :returns: the semi-major axis and uncertainty in units of m
    """
    # We're not using any math/umath funcs here so this will "just work" with ndarrays
    return (G * (m1 + m2) * period**2 / FOUR_PI_SQUARED)**(1/3)


def impact_parameter(r1: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                     inc: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                     e: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                     esinw: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                     secondary: Union[bool, np.ndarray[bool]]=False) \
                        -> Union[float, UFloat, np.ndarray[float], np.ndarray[UFloat]]:
    """
    Calculate the chosen impact parameter using the primary star's fractional
    radius, the orbital inclination and eccentricity, and the e*sin(omega)
    Poincare element.

    :r1: fractional radius of the primary star
    :inc: the orbital inclination in degrees or radians (assumes rad if inc < 2pi)
    :e: the orbital eccentricity
    :esinw: the e*sin(omega) Poincare element
    :secondary: calculate the secondary impact parameter or primary if False
    :returns: the chosen impact parameter
    """
    # Primary eclipse:      (1/r1) * cos(inc) * (1-e^2 / 1+esinw)
    # Secondary eclipse:    (1/r1) * cos(inc) * (1-e^2 / 1-esinw)
    # Only difference is the final divisor so work the common dividend out
    dividend = (1 / r1) * cos(radians(inc)) * (1 - e**2)
    return dividend / (1-esinw if secondary else 1+esinw)


def orbital_inclination(r1: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                        b: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                        e: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                        esinw: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                        secondary: Union[bool, np.ndarray[bool]]=False) \
                            -> Union[float, UFloat, np.ndarray[Union[float, UFloat]]]:
    """
    Calculate the orbital inclination using the primary star's fractional
    radius, the orbital eccentricity and the e*sin(omega) Poincare element
    along with the impact parameter (primary or secondary).

    :r1: fractional radius of the primary star
    :b: the chosen impact parameter
    :e: the orbital eccentricity
    :esinw: the e*sin(omega) Poincare element
    :secondary: whether b is the secondary impact parameter or the primary
    :returns: The inclination in degrees
    """
    # From primary eclipse/impact param:  i = arccos(bP * r1 * (1+esinw)/(1-e^2))
    # From secodary eclipse/impact param: i = arccos(bS * r1 * (1-esinw)/(1-e^2))
    dividend = 1-esinw if secondary else 1+esinw
    return degrees(arccos(b * r1 * dividend / (1 - e**2)))


def ratio_of_eclipse_duration(esinw: Union[float, UFloat, np.ndarray[Union[float, UFloat]]]) \
                                -> Union[float, UFloat, np.ndarray[Union[float, UFloat]]]:
    """
    Calculates the expected (approximate) ratio of eclipse durations
    dS/dP from e*sin(omega).
    
    Uses eqn 5.69 from Hilditch (2001) An Introduction
    to Close Binary Stars reworked in terms of dS/dP

    :esinw: the e*sin(omega) Poincare element
    :returns: the ratio
    """
    return (esinw + 1)/(1 - esinw)


def phase_of_secondary_eclipse(ecosw: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
                               e: Union[float, UFloat, np.ndarray[Union[float, UFloat]]]) \
                                    -> Union[float, UFloat, np.ndarray[Union[float, UFloat]]]:
    """
    Calculates the expected secondary (normalized) phase from e*cos(omega) and
    the eccentricity.

    Uses eqn 5.67 and 5.68 from Hilditch, setting P=1 (normalized) & t_pri=0
    to give phi_sec = t_sec = (X-sinX)/2pi where X=pi+2*atan(ecosw/sqrt(1-e^2))
    """
    x = pi + 2*arctan(ecosw / (1 - e**2)**0.5)
    return (x - sin(x)) / (2 * pi)
