""" Photometry missions. """
# pylint: disable=no-name-in-module
from typing import Union, Tuple
from inspect import getsourcefile
from pathlib import Path
from abc import ABC, abstractmethod
from functools import lru_cache

import numpy as np
import pandas as pd
from pandas import DataFrame

from uncertainties import UFloat
from uncertainties.umath import fsum, exp
from .constants import c, h, k_B

class Mission(ABC):
    """ Base class for mission photemetric characteristics. """
    COL_NAMES = ["lambda", "coefficient"]

    _this_dir = Path(getsourcefile(lambda:0)).parent

    @classmethod
    @lru_cache
    def get_instance(cls, mission_name: str, **kwargs):
        """
        A factory method for getting an instance of a chosen Mission subclass.
        Selects the Mission with a name containing the passed text (i.e.
        TES matches Tess). Raises a KeyError if no match made.

        :model_name: the name of the Mission
        :kwargs: the arguments for the Mission's initializer
        :returns: a cached instance of the chosen Mission
        """
        for subclass in cls.__subclasses__():
            if mission_name.strip().lower() in subclass.__name__.lower():
                return subclass(**kwargs)
        raise KeyError(f"No Mission subclass named like {mission_name}")

    @classmethod
    @abstractmethod
    def get_response_function(cls) -> DataFrame:
        """
        Get the mission's response function, wavelength against efficiency

        :returns: pandas DataFrame indexed on lambda with a coefficient column
        """

    @classmethod
    def get_default_bandpass(cls) -> Tuple[float, float]:
        """
        Gets the default bandpass we use for this mission in nm
        
        :returns: the bandpass tuple in the form (from, to)
        """
        response = cls.get_response_function()
        return (min(response.index), max(response.index))

    @classmethod
    def expected_brightness_ratio(cls,
                                  t_eff_1: Union[float, UFloat],
                                  t_eff_2: Union[float, UFloat],
                                  bandpass: Tuple[float, float] = None) \
                                    -> Union[float, UFloat]:
        """
        Calculate the brightness ratio of two stars (J2/J1) with the passed
        effective temperatures over the requested bandpass making use of this
        mission's response function.

        :t_eff_1: effective temperature of the first star in K
        :t_eff_2: effective temperature of the second star in K
        :bandpass: the range of wavelengths as (u.nm, u.nm) to calculate over
        or, if None, the result of get_default_bandpass() will be used
        :returns: simple ratio of the secondary/primary brightness
        """
        if bandpass is None:
            bandpass = cls.get_default_bandpass()

        response = cls.get_response_function()
        mask = (response.index >= min(bandpass)) & (response.index <= max(bandpass))

        bins = response[mask].index.values
        coeffs = response[mask].coefficient.values

        radiance_1 = fsum(coeffs * cls.__bb_spectral_radiance(t_eff_1, bins))
        radiance_2 = fsum(coeffs * cls.__bb_spectral_radiance(t_eff_2, bins))
        return radiance_2 / radiance_1


    @classmethod
    def __bb_spectral_radiance(cls,
                               temperature: Union[float, UFloat],
                               lambdas: np.ndarray[float]) \
                                    -> np.ndarray[UFloat]:
        """
        Calculates the blackbody spectral radiance:
        power / (area*solid angle*wavelength) at the given temperature and each wavelength

        Uses: B_λ(T) = (2hc^2)/λ^5 * 1/(exp(hc/λkT)-1)
        
        :temperature: the temperature of the body in K
        :wavelengths: the wavelength bins at which of the radiation is to be calculated.
        :returns: NDArray of the calculated radiance, in units of W / m^2 / sr / nm, at each bin
        """
        pt1 = (2 * h * c**2) / lambdas**5
        pt2 = np.array([exp(i) for i in (h * c) / (lambdas * k_B * temperature)]) - 1
        return pt1 / pt2


class Tess(Mission):
    """ Characteristics of the TESS mission. """
    def __init__(self):
        pass

    @classmethod
    def get_default_bandpass(cls) -> Tuple[float, float]:
        return (600, 1000)

    @classmethod
    @lru_cache
    def get_response_function(cls) -> DataFrame:
        """
        The TESS response function, wavelength [nm] against efficiency coeff

        :returns: DataFrame indexed on lambda [nm] with a coefficient column
        """
        file = cls._this_dir / "data/missions/tess/tess-response-function-v2.0.csv"
        return pd.read_csv(file,
                           comment="#",
                           delimiter=",",
                           names=Mission.COL_NAMES,
                           index_col=0)


class Kepler(Mission):
    """ Characteristics of the Kepler mission. """
    def __init__(self):
        pass

    @classmethod
    def get_default_bandpass(cls) -> Tuple[float, float]:
        return (420, 900)

    @classmethod
    @lru_cache
    def get_response_function(cls) -> DataFrame:
        """
        The Kepler response function, wavelength [nm] against efficiency coeff

        :returns: DataFrame indexed on lambda [nm] with a coefficient column
        """
        file = cls._this_dir / "data/missions/kepler/kepler_response_hires1.txt"
        return pd.read_csv(file,
                           comment="#",
                           delim_whitespace=True,
                           names=Mission.COL_NAMES,
                           index_col=0)
