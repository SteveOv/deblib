""" Unit tests for the orbital module. """
import unittest
import numpy as np
import astropy.units as u
from uncertainties import ufloat, UFloat
from uncertainties.unumpy import uarray

from deblib.orbital import orbital_period, semi_major_axis
from deblib.orbital import impact_parameter, orbital_inclination
from deblib.orbital import ratio_of_eclipse_duration, phase_of_secondary_eclipse
from deblib.orbital import eclipse_duration, estimate_ecosw, estimate_esinw

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


    #
    # Test eclipse_duration(period, sum_r, inc, e, esinw, secondary) -> dur
    #
    def test_eclipse_duration_basic(self):
        """ Basic happy path tests of eclipse_duration() to assert handling of args """
        for (per,       sum_r,  inc,    e,      esinw,  sec,    exp_dur,    msg) in [
            (24.5924,   0.099,  88.359, 0.188,  0.177,  False,  0.619,      "AI Phe primary with floats"),
            (24.5924,   0.099,  88.359, 0.188,  0.177,  True,   0.885,      "AI Phe secondary with floats"),
            (ufloat(24.5924, 0.0010),
                        ufloat(0.099, 0.001),
                               ufloat(88.359, 0.007),
                                        ufloat(0.188, 0.001),
                                                ufloat(0.177, 0.001),
                                                        False,  ufloat(0.619, 0.007),
                                                                            "AI Phe primary with ufloats"),
            (np.array([24.5924]*3),
                        np.array([0.099]*3),
                                np.array([88.359]*3),
                                        np.array([0.188]*3),
                                                np.array([0.177]*3),
                                                        False,
                                                                np.array([0.619]*3),
                                                                            "AI Phe primary with ndarray[floats]"),
            (uarray([24.5924]*3, 0.0010),
                        uarray([0.099]*3, 0.001),
                                uarray([88.359]*3, 0.007),
                                        uarray([0.188]*3, 0.001),
                                                uarray([0.177]*3, 0.001),
                                                        False,
                                                                uarray([0.619]*3, 0.007),
                                                                            "AI Phe primary with ndarray[UFloats]"),
        ]:
            with self.subTest(msg):
                dur = eclipse_duration(per, sum_r, inc, e, esinw, sec)
                for expected, actual in zip(exp_dur if isinstance(exp_dur, np.ndarray) else np.array([exp_dur]),
                                            dur if isinstance(dur, np.ndarray) else np.array([dur])):
                    actual_nom = actual.n if isinstance(actual, UFloat) else actual
                    expected_nom = expected.n if isinstance(expected, UFloat) else expected
                    self.assertAlmostEqual(expected_nom, actual_nom, 3)

                    actual_std = actual.s if isinstance(actual, UFloat) else 0
                    expected_std = expected.s if isinstance(expected, UFloat) else 0
                    self.assertAlmostEqual(expected_std, actual_std, 3)


    #
    # Test estimate_ecosw(phis, phip) -> ecosw
    #
    def test_estimate_ecosw_basic(self):
        """ Basic happy path tests of estimate_ecosw() to assert calculations & handling of types of args """
        for (phis,                      phip,                   exp_ecosw,                      msg) in [
            (.499,                      0,                      -0.0017,                        "CM Dra with floats"),
            (.599,                      .1,                     -0.0017,                        "CM Dra with floats - relative phase 1"),
            (1.,                        .501,                   -0.0017,                        "CM Dra with floats - relative phase 2"),

            (0.499,                     None,                   -0.0017,                        "CM Dra with float & default phip"),
            (ufloat(.499, .001),        ufloat(0.0, 0.001),     ufloat(-0.0017, .002),          "CM Dra with ufloats"),
            (ufloat(.499, .001),        None,                   ufloat(-0.0017, .002),          "CM Dra with ufloat & default phip"),
            (np.array([.499, .499]),    np.array([0.0, 0.0]),   np.array([-0.0017, -0.0017]),   "CM Dra with array[float]"),
            (np.array([.499, .499]),    None,                   np.array([-0.0017, -0.0017]),   "CM Dra with array[float] & default phip"),

            (.458,                      0,                      -0.066,                         "AI Phe"),
            (.788,                      0,                      0.452,                          "AN Cam"),
        ]:
            with self.subTest(msg):
                if phip is not None:
                    ecosw = estimate_ecosw(phis, phip)
                else:
                    ecosw = estimate_ecosw(phis)

                for expected, actual in zip(exp_ecosw if isinstance(exp_ecosw, np.ndarray) else np.array([exp_ecosw]),
                                            ecosw if isinstance(ecosw, np.ndarray) else np.array([ecosw])):
                    actual_nom = actual.n if isinstance(actual, UFloat) else actual
                    expected_nom = expected.n if isinstance(expected, UFloat) else expected
                    self.assertAlmostEqual(expected_nom, actual_nom, 3)

                    actual_std = actual.s if isinstance(actual, UFloat) else 0
                    expected_std = expected.s if isinstance(expected, UFloat) else 0
                    self.assertAlmostEqual(expected_std, actual_std, 3)


    #
    # Test estimate_esinw(dp, ds) -> esinw
    #
    def test_estimate_esinw_basic(self):
        """ Basic happy path tests of estimate_esinw() to assert calculations & handling of types of args """
        for (durp,                      durs,                       exp_esinw,                  msg) in [
            (.044,                      .045,                       .011,                       "CM Dra with floats of phases"),
            (.0554,                     .0560,                      .005,                       "CM Dra with floats of days"),
            (ufloat(.0554, .0001),      ufloat(.0560, .0001),       ufloat(.0050, .0013),       "CM Dra with ufloats of days"),
            (np.array([.044, .0554]),   np.array([.045, .0560]),    np.array([.011, .005]),     "CM Dra with array[float]"),

            (.619,                      .885,                       .177,                       "AI Phe"),
            (.558,                      .711,                       .121,                       "AN Cam"),
        ]:
            with self.subTest(msg):
                esinw = estimate_esinw(durp, durs)

                for expected, actual in zip(exp_esinw if isinstance(exp_esinw, np.ndarray) else np.array([exp_esinw]),
                                            esinw if isinstance(esinw, np.ndarray) else np.array([esinw])):
                    actual_nom = actual.n if isinstance(actual, UFloat) else actual
                    expected_nom = expected.n if isinstance(expected, UFloat) else expected
                    self.assertAlmostEqual(expected_nom, actual_nom, 3)

                    actual_std = actual.s if isinstance(actual, UFloat) else 0
                    expected_std = expected.s if isinstance(expected, UFloat) else 0
                    self.assertAlmostEqual(expected_std, actual_std, 3)



if __name__ == "__main__":
    unittest.main()
