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
    :r: the stellar radius in units of m
    :returns: the log(g)) value and uncertainty
    """
    # Starts in SI units of m/s^2 then to cgs units cm/s^2
    return log10((G * m / r**2) * 100)


def black_body_spectral_radiance(temperature: Union[float, UFloat],
                                 lambdas: np.ndarray[float]) \
                                    -> np.ndarray[UFloat]:
    """
    Calculates the blackbody spectral radiance at given wavelengths [nm] at
    the given temperature [K].

    - BB radiance: B(v, T) = (2hv^3)/c^2 * 1/(exp(hv/kT)-1)  [W / (m^2 sr Hz)]

    - which for λ is: B(λ, T) = (2e36 hc^2)/λ^5 * 1/(exp(1e9 hc/λkT)-1)  [W / (m^2 sr nm)]
    
    where where λ [nm] = 10^9 c/v

    :temperature: the temperature of the body in K
    :lambdas: the wavelength bins (in nm) at which of the radiation is to be calculated.
    :returns: NDArray of the calculated radiance for each bin, in units of W / (m^2 sr nm)
    """
    # This approach reproduces the results of the poc implementation which would
    # have included implicit support for lambda [nm] through the use of astropy units.
    pt1 = (2e36 * h * c**2) / lambdas**5
    pt2 = exp((1e9 * h * c) / (lambdas * k_B * temperature)) - 1
    return pt1 / pt2
