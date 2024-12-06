""" Utility functions for Stellar relations. """
# pylint: disable=no-name-in-module, no-member
from typing import Union

import numpy as np
from uncertainties.umath import log10, exp
from uncertainties import UFloat

from .constants import G, h, c, k_B


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


def black_body_spectral_radiance(temperature: Union[float, UFloat],
                                 lambdas: np.ndarray[float]) \
                                    -> np.ndarray[UFloat]:
    """
    Calculates the blackbody spectral radiance:
    power / (area*solid angle*wavelength) at the given temperature and each wavelength

    Uses: B_λ(T) = (2hc^2)/λ^5 * 1/(exp(hc/λkT)-1)
    
    :temperature: the temperature of the body in K
    :lambdas: the wavelength bins at which of the radiation is to be calculated.
    :returns: NDArray of the calculated radiance, in units of W / m^2 / sr / nm, at each bin
    """
    pt1 = (2 * h * c**2) / lambdas**5
    pt2 = np.array([exp(i) for i in (h * c) / (lambdas * k_B * temperature)]) - 1
    return pt1 / pt2
