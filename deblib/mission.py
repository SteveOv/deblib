""" Photometry missions. """
# pylint: disable=no-name-in-module
from typing import Union, Tuple
from inspect import getsourcefile
from pathlib import Path
from abc import ABC, abstractmethod
from functools import lru_cache

import numpy as np

from uncertainties import UFloat
from uncertainties.umath import fsum

from .stellar import black_body_spectral_radiance

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
    def get_response_function(cls) -> np.ndarray:
        """
        Get the mission's response function, wavelength against efficiency

        :returns: structured array with lambda [nm] and coefficient columns
        """

    @classmethod
    def get_default_bandpass(cls) -> Tuple[float, float]:
        """
        Gets the default bandpass we use for this mission in nm
        
        :returns: the bandpass tuple in the form (from, to)
        """
        response = cls.get_response_function()
        return (response["lambda"].min(), response["lambda"].max())

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
        :bandpass: the range of wavelengths as [nm] to calculate over
        or, if None, the result of get_default_bandpass() will be used
        :returns: simple ratio of the secondary/primary brightness
        """
        if bandpass is None:
            bandpass = cls.get_default_bandpass()

        rf = cls.get_response_function()
        mask = (rf["lambda"] >= min(bandpass)) & (rf["lambda"] <= max(bandpass))
        bins = rf[mask]["lambda"]
        coeffs = rf[mask]["coefficient"]

        radiance_1 = fsum(coeffs * black_body_spectral_radiance(t_eff_1, bins))
        radiance_2 = fsum(coeffs * black_body_spectral_radiance(t_eff_2, bins))
        return radiance_2 / radiance_1


class Tess(Mission):
    """ Characteristics of the TESS mission. """
    def __init__(self):
        pass

    @classmethod
    def get_default_bandpass(cls) -> Tuple[float, float]:
        return (600, 1000)

    @classmethod
    @lru_cache
    def get_response_function(cls) -> np.ndarray:
        """
        The TESS response function, wavelength [nm] against efficiency coeff

        :returns: structured array with lambda [nm] and coefficient columns
        """
        file = cls._this_dir / "data/missions/tess/tess-response-function-v2.0.csv"
        return np.genfromtxt(file, float, "#", ",", skip_header=7, names=Mission.COL_NAMES)


class Kepler(Mission):
    """ Characteristics of the Kepler mission. """
    def __init__(self):
        pass

    @classmethod
    def get_default_bandpass(cls) -> Tuple[float, float]:
        return (420, 900)

    @classmethod
    @lru_cache
    def get_response_function(cls) -> np.ndarray:
        """
        The Kepler response function, wavelength [nm] against efficiency coeff

        :returns: structured array with lambda [nm] and coefficient columns
        """
        file = cls._this_dir / "data/missions/kepler/kepler_response_hires1.txt"
        return np.genfromtxt(file, float, "#", skip_header=9, names=Mission.COL_NAMES)
