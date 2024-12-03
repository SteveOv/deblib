""" Unit tests for the orbital module. """
# pylint: disable=no-name-in-module, no-member
import unittest
import astropy.units as u
from uncertainties import ufloat, UFloat

from deblib.orbital import orbital_period, semi_major_axis
from deblib.orbital import impact_parameter, orbital_inclination, EclipseType

# Fiducial units to SI
M_EARTH = (1 * u.earthMass).to(u.kg).value
M_SOL = (1 * u.solMass).to(u.kg).value
R_SOL = (1 * u.solRad).to(u.m).value
AU = (1 * u.au).to(u.m).value
YEAR = (1 * u.yr).to(u.s).value

# pylint: disable=too-many-public-methods, no-member, line-too-long
class Testorbital(unittest.TestCase):
    """ Unit tests for the orbital module. """

    #
    # Test orbital_period(m1, m2, a) -> [s]
    #
    def test_orbital_period_sol_values(self):
        """ Basic test of orbital_period() with/without uncertainties """
        for m1, m2, a, exp_period in [
            (1 * M_SOL, 1 * M_EARTH, 1 * AU, 365.256),
            (ufloat(1 * M_SOL, 1e14), ufloat(1 * M_EARTH, 1e12), ufloat(1 * AU, 1e8), 365.256),
            (1 * M_SOL, 1 * M_EARTH, ufloat(1 * AU, 1e8), 365.256),
        ]:
            period = orbital_period(m1, m2, a) / 86400
            print(f"period={period:.6f}")
            period_nom = period.nominal_value if isinstance(period, UFloat) else period
            self.assertAlmostEqual(exp_period, period_nom, 2)

    #
    # Test semi_major_axis(m1, m2, period) -> [m]
    #
    def test_semi_major_axis_sol_values(self):
        """ Basic test of semi_major_axis() with/without uncertainties """
        for m1, m2, period, exp_a in [
            (1 * M_SOL, 1 * M_EARTH, 1 * YEAR, 1),
            (ufloat(1 * M_SOL, 1e14), ufloat(1 * M_EARTH, 1e10), ufloat(1 * YEAR, 1e2), 1),
            (ufloat(1 * M_SOL, 1e14), ufloat(1 * M_EARTH, 1e10), 1 * YEAR, 1),
        ]:
            a = semi_major_axis(m1, m2, period) / AU
            print(f"semi_major_axis={a:.6f}")
            a_nom = a.nominal_value if isinstance(a, UFloat) else a
            self.assertAlmostEqual(exp_a, a_nom, 4)

    #
    # Tests impact_parameter(rA, inc, e, [omega], [esinw], [eclipse=EclipseType])
    #
    def test_impact_parameter_circular_edge_on_both_eclipses(self):
        """ Basic test of impact_parameter() with/without uncertainties """
        for r1, inc, e, esinw, eclipse, exp_b in [
            (R_SOL/AU, 90, 0, 0, EclipseType.PRIMARY, 0.),
            (R_SOL/AU, 90, 0, 0, EclipseType.SECONDARY, 0.),
            (ufloat(R_SOL/AU, 0.0001), ufloat(90, 0.001), 0, 0, EclipseType.PRIMARY, 0.),
            (ufloat(R_SOL/AU, 0.0001), 90, ufloat(0, 0.001), 0, EclipseType.SECONDARY, 0.),
        ]:
            b = impact_parameter(r1, inc, e, esinw, eclipse)
            print(f"b={b:.6f}")
            b_nom = b.nominal_value if isinstance(b, UFloat) else b
            self.assertAlmostEqual(exp_b, b_nom, 12)

    #
    # Test orbital_inclination(r1, b, e, esinw, [eclipse=EclipseType]) -> [deg]
    #
    def test_orbital_inclination_on_edge_on_orbit(self):
        """ Basic test of orbital_inclination() with/without uncertainties """
        for r1, b, e, esinw, eclipse, exp_inc in [
            (R_SOL/AU, 0, 0, 0, EclipseType.PRIMARY, 90.),
            (R_SOL/AU, 0, 0, 0, EclipseType.SECONDARY, 90.),
            (ufloat(R_SOL/AU, 0.001), ufloat(0, 0.001), 0, 0, EclipseType.PRIMARY, 90.),
            (ufloat(R_SOL/AU, 0.001), ufloat(0, 0.001), 0, 0, EclipseType.SECONDARY, 90.),
        ]:
            inc = orbital_inclination(r1, b, e, esinw, eclipse=eclipse)
            print(f"inc={inc:.6f}")
            inc_nom = inc.nominal_value if isinstance(inc, UFloat) else inc
            self.assertEqual(exp_inc, inc_nom)
