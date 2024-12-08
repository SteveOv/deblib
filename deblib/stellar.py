""" Utility functions for Stellar relations. """
from typing import Union

import numpy as np
from uncertainties import UFloat

from .constants import G, h, c, k_B
from .vmath import log10, exp

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
    # Starts in SI units of m/s^2 then to cgs units cm/s^2
    return log10((G * m / r**2) * 100)


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
    inr = (h * c) / (lambdas * k_B * temperature)

    # This is what is happening in the old code; effectively "undoing" the inr units of m / nm.
    # Replicating the behaviour for consistency during cutover to this new library, however I think
    # this needs revisiting and and instead we should using the commented out line. Raised issue #1.
    pt2 = (1 / (exp(inr / 1e-9) - 1))
    #pt2 = (1 / (exp(inr) - 1))

    return pt1 * pt2
