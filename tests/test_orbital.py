""" Unit tests for the orbital module. """
import unittest
import numpy as np
import astropy.units as u
from uncertainties import ufloat, UFloat
from uncertainties.unumpy import uarray

from deblib.orbital import orbital_period, semi_major_axis
from deblib.orbital import impact_parameter, orbital_inclination
from deblib.orbital import ratio_of_eclipse_duration, phase_of_secondary_eclipse

# Fiducial units to SI
# pylint: disable=no-name-in-module, no-member
M_EARTH = (1 * u.earthMass).to(u.kg).value
M_SOL = (1 * u.solMass).to(u.kg).value
R_SOL = (1 * u.solRad).to(u.m).value
AU = (1 * u.au).to(u.m).value
YEAR = (1 * u.yr).to(u.s).value


class Testorbital(unittest.TestCase):
    """ Unit tests for the orbital module. """
    # pylint: disable=too-many-public-methods, line-too-long

    #
    # Test orbital_period(m1, m2, a) -> period
    #
    def test_orbital_period_basic(self):
        """ Basic happy path tests of orbital_period() to assert handling of args """
        for (m1,                    m2,                         a,                  exp_period) in [
            (M_SOL,                 M_EARTH,                    AU,                 365.256),
            (ufloat(M_SOL, 0),      ufloat(M_EARTH, 0),         ufloat(AU, 0),      365.256),
            (np.array([M_SOL]*10),  np.array([M_EARTH]*10),     np.array([AU]*10),  np.array([365.256]*10)),
            (uarray([M_SOL]*10, 0), uarray([M_EARTH]*10, 0),    uarray([AU]*10, 0), np.array([365.256]*10)),
        ]:
            period = orbital_period(m1, m2, a) / 86400
            for expected, actual in zip(exp_period if isinstance(exp_period, np.ndarray) else np.array([exp_period]),
                                        period if isinstance(period, np.ndarray) else np.array([period])):
                self.assertAlmostEqual(expected, actual.nominal_value, 2)

    #
    # Test semi_major_axis(m1, m2, period) -> a
    #
    def test_semi_major_axis_basic(self):
        """ Basic happy path tests of semi_major_axis() to assert handling of args """
        for (m1,                    m2,                         period,                 exp_a) in [
            (M_SOL,                 M_EARTH,                    YEAR,                   1),
            (ufloat(M_SOL, 0),      ufloat(M_EARTH, 0),         ufloat(YEAR, 0),        1),
            (np.array([M_SOL]*10),  np.array([M_EARTH]*10),     np.array([YEAR]*10),    np.array([1]*10)),
            (uarray([M_SOL]*10, 0), uarray([M_EARTH]*10, 0),    uarray([YEAR]*10, 0),   np.array([1]*10)),
        ]:
            a = semi_major_axis(m1, m2, period) / AU
            for expected, actual in zip(exp_a if isinstance(exp_a, np.ndarray) else np.array([exp_a]),
                                        a if isinstance(a, np.ndarray) else np.array([a])):
                self.assertAlmostEqual(expected, actual.nominal_value, 4)

    #
    # Tests impact_parameter(rA, inc, e, esinw, secondary:bool=False) -> b
    #
    def test_impact_parameter_basic(self):
        """ Basic happy path tests of impact_parameter() to assert handling of args """
        for (r1,                        inc,                e,                  esinw,              secondary,  exp_b) in [
            (R_SOL/AU,                  90,                 0,                  0,                  False,      0.),
            (R_SOL/AU,                  90,                 0,                  0,                  True,       0.),
            (ufloat(R_SOL/AU, 0),       ufloat(90, 0),      ufloat(0, 0),       ufloat(0, 0),       False,      0.),
            (ufloat(R_SOL/AU, 0),       ufloat(90, 0),      ufloat(0, 0),       ufloat(0, 0),       True,       0.),
            (np.array([R_SOL/AU]*9),    np.array([90]*9),   np.array([0]*9),    np.array([0]*9),    False,      np.array([0.])),
            (np.array([R_SOL/AU]*9),    np.array([90]*9),   np.array([0]*9),    np.array([0]*9),    True,       np.array([0.])),
            (uarray([R_SOL/AU]*9, 0),   uarray([90]*9, 0),  uarray([0]*9, 0),   uarray([0]*9, 0),   False,      np.array([0.])),
            (uarray([R_SOL/AU]*9, 0),   uarray([90]*9, 0),  uarray([0]*9, 0),   uarray([0]*9, 0),   True,       np.array([0.])),
        ]:
            b = impact_parameter(r1, inc, e, esinw, secondary)
            for expected, actual in zip(exp_b if isinstance(exp_b, np.ndarray) else np.array([exp_b]),
                                        b if isinstance(b, np.ndarray) else np.array([b])):
                actual_nom = actual.nominal_value if isinstance(actual, UFloat) else actual
                self.assertAlmostEqual(expected, actual_nom, 12)

    #
    # Test orbital_inclination(r1, b, e, esinw, secondary:bool=False) -> i
    #
    def test_orbital_inclination_basic(self):
        """ Basic happy path tests of orbital_inclination() to assert handling of args """
        for (r1,                        b,                  e,                  esinw,              secondary,  exp_inc) in [
            (R_SOL/AU,                  0,                  0,                  0,                  False,      90.),
            (R_SOL/AU,                  0,                  0,                  0,                  True,       90.),
            (ufloat(R_SOL/AU, 0),       ufloat(0, 0),       ufloat(0, 0),       ufloat(0, 0),       False,      90.),
            (ufloat(R_SOL/AU, 0),       ufloat(0, 0),       ufloat(0, 0),       ufloat(0, 0),       True,       90.),
            (np.array([R_SOL/AU]*9),    np.array([0]*9),    np.array([0]*9),    np.array([0]*9),    False,      np.array([90.])),
            (np.array([R_SOL/AU]*9),    np.array([0]*9),    np.array([0]*9),    np.array([0]*9),    True,       np.array([90.])),
            (uarray([R_SOL/AU]*9, 0),   uarray([0]*9, 0),   uarray([0]*9, 0),   uarray([0]*9, 0),   False,      np.array([90.])),
            (uarray([R_SOL/AU]*9, 0),   uarray([0]*9, 0),   uarray([0]*9, 0),   uarray([0]*9, 0),   True,       np.array([90.])),
        ]:
            inc = orbital_inclination(r1, b, e, esinw, secondary)
            for expected, actual in zip(exp_inc if isinstance(exp_inc, np.ndarray) else np.array([exp_inc]),
                                        inc if isinstance(inc, np.ndarray) else np.array([inc])):
                actual_nom = actual.nominal_value if isinstance(actual, UFloat) else actual
                self.assertEqual(expected, actual_nom)


    #
    # Test ratio_of_eclipse_duration(esinw) -> ~dS/sP
    #
    def test_ratio_of_eclipse_duration_basic(self):
        """ Basic happy path tests of ratio_of_eclipse_duration() to assert handling of args """
        for (esinw,              exp_dur) in [
            (0,                  1.),
            (ufloat(0, 0),       1.),
            (np.array([0]*9),    np.array([1.])),
            (uarray([0]*9, 0),   np.array([1.])),
        ]:
            dur = ratio_of_eclipse_duration(esinw)
            for expected, actual in zip(exp_dur if isinstance(exp_dur, np.ndarray) else np.array([exp_dur]),
                                        dur if isinstance(dur, np.ndarray) else np.array([dur])):
                actual_nom = actual.nominal_value if isinstance(actual, UFloat) else actual
                self.assertEqual(expected, actual_nom)


    #
    # Test phase_of_secondary_eclipse(ecosw, e) -> phiS
    #
    def test_phase_of_secondary_eclipse_basic(self):
        """ Basic happy path tests of phase_of_secondary_eclipse() to assert handling of args """
        for (ecosw,              e,                 exp_phis) in [
            (0,                  0,                 0.5),
            (ufloat(0, 0),       ufloat(0, 0),      0.5),
            (np.array([0]*9),    np.array([0]*9),   np.array([0.5])),
            (uarray([0]*9, 0),   uarray([0]*9, 0),  np.array([0.5])),
        ]:
            phis = phase_of_secondary_eclipse(ecosw, e)
            for expected, actual in zip(exp_phis if isinstance(exp_phis, np.ndarray) else np.array([exp_phis]),
                                        phis if isinstance(phis, np.ndarray) else np.array([phis])):
                actual_nom = actual.nominal_value if isinstance(actual, UFloat) else actual
                self.assertEqual(expected, actual_nom)

if __name__ == "__main__":
    unittest.main()
