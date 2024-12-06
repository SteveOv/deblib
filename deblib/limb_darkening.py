""" Module publishing methods for lookup up Limb Darkening coefficients. """
from typing import Tuple, List
from inspect import getsourcefile
from pathlib import Path
from functools import lru_cache

import numpy as np

from .utility import round_to_nearest

_this_dir = Path(getsourcefile(lambda:0)).parent


def lookup_quad_coefficients(logg: float,
                             t_eff: float,
                             mission: str="TESS") \
                                -> Tuple[float, float]:
    """
    Get the quad limb darkening (a, b) coefficients nearest to the passed
    log(g) and T_eff values. Data from Claret (A/A&A/618/A20) table 5.

    :logg: the requested log(g) - nearest value will be used
    :t_eff: the requested T_eff in K - nearest value will be used
    :mission: currently only supports TESS or Kepler coefficients
    :returns: tuple (a, b) where a is the linear and b the quadratic coefficient
    """
    table = __quad_ld_coeffs_table(mission)
    return __lookup_nearest_coeffs(table, logg, t_eff, ["a", "b"])


def lookup_pow2_coefficients(logg: float,
                             t_eff: float,
                             mission: str="TESS") \
                                -> Tuple[float, float]:
    """
    Get the quad limb darkening (a, b) coefficients nearest to the passed
    log(g) and T_eff values. Data from Claret (A/A&A/618/A20) table 5.

    :logg: the requested log(g) - nearest value will be used
    :t_eff: the requested T_eff in K - nearest value will be used
    :mission: currently only supports TESS or Kepler coefficients
    :returns: tuple (a, b) where a is the linear and b the quadratic coefficient
    """
    table = __pow2_ld_coeffs_table(mission)
    return __lookup_nearest_coeffs(table, logg, t_eff, ["g", "h"])


def __lookup_nearest_coeffs(table: np.ndarray,
                            logg: float,
                            t_eff: float,
                            coeffs_fields: List) \
                                -> Tuple[float]:
    """
    Performs a nearest match lookup with logg and t_eff to get a tuple of the
    coefficient values in fields. 
    """
    # The logg values are in 0.5 dex steps
    logg = round_to_nearest(logg, 0.5)
    logg = max(table["logg"].min(), logg)
    logg = min(table["logg"].max(), logg)
    masked = table[(table["logg"] == logg) & (table["Z"] == 0.0)]

    # Currently don't filter on Z as they're all 0.0

    # Finally hone in on the nearest Teff value
    coeffs = masked[np.argmin(abs(masked["Teff"] - t_eff))][coeffs_fields]
    return tuple(coeffs)

# Using funcs with lru_cache to gives us caching and lazy loading of these data
@lru_cache
def __quad_ld_coeffs_table(mission: str="TESS") -> np.ndarray[float]:
    """
    The lookup table for quad LD coefficients from Claret (A/A&A/618/A20).
    """
    # These are for solar metallicity with v.tu=2 km/s
    data_files = {
        # TESS quad coeffs in Tables 4 (PHOENIX-DFIFT) & 5 (PHOENIX-COND)
        "TESS": _this_dir / "data/limb_darkening/quad/J_A+A_618_A20/table5.dat",
        # Kepler quad coeffs in Tables 8 (PHOENIX-DFIFT) & 9 (PHOENIX-COND)
        "Kepler": _this_dir / "data/limb_darkening/quad/J_A+A_618_A20/table9.dat",
    }
    return np.genfromtxt(data_files[mission], float, "#",
                         usecols=[0, 1, 2, 4, 5],
                         names=["logg", "Teff", "Z", "a", "b"])

@lru_cache
def __pow2_ld_coeffs_table(mission: str="TESS") -> np.ndarray[float]:
    """
    The lookup table for power-2 LD coefficients from Claret (J/A+A/674/A63).
    """
    # Table 1 gives the M1 coeffs derived from PHOENIX spherically symmetric models
    # for Gaia (G_bp, G, G_rp), Kepler, TESS & CHEOPS.
    data_file = _this_dir / "data/limb_darkening/pow2/J_A+A_674_A63/table1.dat"
    g_h_columns = { # [g, h]        and equivalent physical cols in the data file
        "TESS":     [8, 14],        # 76-87 & 154-165
        "Kepler":   [7, 13],        # 63-74 & 141-152
        #"CHEOPS":   [9, 15],        # 89-100 & 167-178
    }
    return np.genfromtxt(data_file, float, "#",
                         usecols=[0, 1, 2] + g_h_columns[mission],
                         names=["logg", "Teff", "Z", "g", "h"])
