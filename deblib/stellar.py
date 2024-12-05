""" Utility functions for Stellar relations. """
# pylint: disable=no-name-in-module, no-member
from typing import Union

import numpy as np
from uncertainties.umath import log10
from uncertainties import UFloat

from .constants import G

def log_g(m: Union[float, UFloat, np.ndarray[Union[float, UFloat]]],
          r: Union[float, UFloat, np.ndarray[Union[float, UFloat]]]) \
            -> Union[UFloat, np.ndarray[UFloat]]:
    """ 
    Calculate log(g) at the surface of a body with the given mass and radius. 

    log(g) = log((Gm/r^2) [cgs])

    Because G has an uncertainty, the result will always have an uncertainty

    :m: the stellar mass in units of kg
    :r: the stellar radius in units of r
    :returns: the log(g)) value and uncertainty
    """
    if isinstance(m, np.ndarray):
        # This function uses non-vectorized math/umath functions so we iterate
        result = np.array([log_g(*args) for args in zip(m, r)])
    else:
        # Starts in SI units of m/s^2 then to cgs units cm/s^2
        result = log10((G * m / r**2) * 100)
    return result
