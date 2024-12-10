""" Unit tests for the limb_darkening module. """
import unittest

from deblib import limb_darkening

# pylint: disable=too-many-public-methods, line-too-long, protected-access
class Testlimbdarkening(unittest.TestCase):
    """ Unit tests for the limb_darkening module. """

    # Expected quad & TESS lookup (as 1 based line numbers in J_A+A_618_A20/table5.dat)
    # and quad & Kepler lookup (as 1 based line numbers in J_A+A_618_A20/table9.dat)
    quad_line_4_0_6500 = 330
    quad_line_4_0_7200 = 378
    quad_line_5_0_4900 = 212
    quad_line_5_0_5100 = 220
    quad_line_min_2300 = 1
    quad_line_max_12000 = 574
    quad_line_4_0_min = 4
    quad_line_4_0_max = 570

    # Expected pow2 & TESS/Kepler lookup (as 1 based line numbers in J_A+A_674_A63/table1.dat)
    pow2_line_4_0_6500 = 523
    pow2_line_6_0_6500 = 527
    pow2_line_4_0_7200 = 588
    pow2_line_5_0_4900 = 347
    pow2_line_5_0_5100 = 360
    pow2_line_min_2300 = 1
    pow2_line_max_12000 = 823
    pow2_line_4_0_min = 9
    pow2_line_4_0_max = 819

    #
    # TESS Quadratic LD Coeffs: lookup_quad_ld_coeffs(logg, T_eff, mission) -> (float, float)
    #
    def test_lookup_quad_ld_coeffs_tess_basic(self):
        """ Tests lookup_quad_ld_coeffs(logg, t_eff, "TESS") """
        reference_data = limb_darkening._quad_ld_coeffs_table("TESS")
        for (logg,  t_eff,      exp_coeffs_line) in [
            # Test finding correct data in the range where logg steps are 0.5 and teff are 100 K
            (4.0,   6500.0,     self.quad_line_4_0_6500),
            (4.24,  6500.0,     self.quad_line_4_0_6500),
            (3.76,  6500.0,     self.quad_line_4_0_6500),
            (4.0,   6549.9,     self.quad_line_4_0_6500),
            (4.0,   6450.1,     self.quad_line_4_0_6500),

            # These test the region where the temp steps change from 100 to 200 K (temps >=7000).
            # They're expected to return the values for logg 4.0, T_eff 7200 (no 7100, 7300 rows).
            (4.0,   7100.1,     self.quad_line_4_0_7200),
            (4.0,   7299.0,     self.quad_line_4_0_7200),

            # There's a gap in the coeffs between Teff 4900 and 5100 K
            # Test the case where we need to round away from 5000, otherwise we get a KeyError.
            (4.81,  4956.7,     self.quad_line_5_0_4900),
            (5.24,  5021.3,     self.quad_line_5_0_5100),

            # The logg covers [2.5, 6.0] and Teff [2300, 12000] K
            # Test the cases where request outside this range -> expect to use limts
            (0.0,   2300.0,     self.quad_line_min_2300),
            (6.5,   12000.0,    self.quad_line_max_12000),
            (4.0,   2000.0,     self.quad_line_4_0_min),
            (4.0,   12600.0,    self.quad_line_4_0_max),
        ]:
            exp_coeffs = tuple(reference_data[exp_coeffs_line - 1][["a", "b"]])
            coeffs = limb_darkening.lookup_quad_coefficients(logg, t_eff, "TESS")
            self.assertEqual(exp_coeffs, coeffs,
                             f"TESS quad coeffs {coeffs} mismatch data file ln {exp_coeffs_line}")

    def test_lookup_quad_ld_coeffs_kepler_basic(self):
        """ Tests lookup_quad_ld_coeffs(logg, t_eff, "Kepler") """
        reference_data = limb_darkening._quad_ld_coeffs_table("Kepler")
        for (logg,  t_eff,      exp_coeffs_line) in [
            # Test finding correct data in the range where logg steps are 0.5 and teff are 100 K
            (4.0,   6500.0,     self.quad_line_4_0_6500),
            (4.24,  6500.0,     self.quad_line_4_0_6500),
            (3.76,  6500.0,     self.quad_line_4_0_6500),
            (4.0,   6549.9,     self.quad_line_4_0_6500),
            (4.0,   6450.1,     self.quad_line_4_0_6500),

            # These test the region where the temp steps change from 100 to 200 K (temps >=7000).
            # They're expected to return the values for logg 4.0, T_eff 7200 (no 7100, 7300 rows).
            (4.0,   7100.1,     self.quad_line_4_0_7200),
            (4.0,   7299.0,     self.quad_line_4_0_7200),

            # There's a gap in the coeffs between Teff 4900 and 5100 K
            # Test the case where we need to round away from 5000, otherwise we get a KeyError.
            (4.81,  4956.7,     self.quad_line_5_0_4900),
            (5.24,  5021.3,     self.quad_line_5_0_5100),

            # The logg covers [2.5, 6.0] and Teff [2300, 12000] K
            # Test the cases where request outside this range -> expect to use limts
            (0.0,   2300.0,     self.quad_line_min_2300),
            (6.5,   12000.0,    self.quad_line_max_12000),
            (4.0,   2000.0,     self.quad_line_4_0_min),
            (4.0,   12600.0,    self.quad_line_4_0_max),
        ]:
            exp_coeffs = tuple(reference_data[exp_coeffs_line - 1][["a", "b"]])
            coeffs = limb_darkening.lookup_quad_coefficients(logg, t_eff, "Kepler")
            self.assertEqual(exp_coeffs, coeffs,
                             f"Kepler quad coeffs {coeffs} mismatch data file ln {exp_coeffs_line}")


    #
    # TESS power-2 LD Coeffs: lookup_pow2_ld_coeffs(logg, T_eff, mission) -> (float, float)
    #
    def test_lookup_pow2_ld_coeffs_tess_basic(self):
        """ Tests lookup_pow2_coefficients(logg, t_eff, "TESS") """
        reference_data = limb_darkening._pow2_ld_coeffs_table("TESS")
        for (logg,  t_eff,      exp_coeffs_line) in [
            # Test finding correct data in the range where logg steps are 0.5 and teff are 100 K
            (4.0,   6500.0,     self.pow2_line_4_0_6500),
            (4.24,  6500.0,     self.pow2_line_4_0_6500),
            (3.76,  6500.0,     self.pow2_line_4_0_6500),
            (4.0,   6549.9,     self.pow2_line_4_0_6500),
            (4.0,   6450.1,     self.pow2_line_4_0_6500),

            # These test the region where the temp steps change from 100 to 200 K (temps >=7000).
            # They're expected to return the values for logg 4.0, T_eff 7200 (no 7100, 7300 rows).
            (4.0,   7100.1,     self.pow2_line_4_0_7200),
            (4.0,   7299.0,     self.pow2_line_4_0_7200),

            # There's a gap in the coeffs between Teff 4900 and 5100 K
            # Test the case where we need to round away from 5000, otherwise we get a KeyError.
            (4.81,  4956.7,     self.pow2_line_5_0_4900),
            (5.24,  5021.3,     self.pow2_line_5_0_5100),

            # The logg covers [0.0, 6.0] and Teff [2300, 12000] K
            # Test the cases where request outside this range -> expect to use limts
            (0.0,   2300.0,     self.pow2_line_min_2300),
            (6.5,   12000.0,    self.pow2_line_max_12000),
            (4.0,   2000.0,     self.pow2_line_4_0_min),
            (4.0,   12600.0,    self.pow2_line_4_0_max),
        ]:
            exp_coeffs = tuple(reference_data[exp_coeffs_line - 1][["g", "h"]])
            coeffs = limb_darkening.lookup_pow2_coefficients(logg, t_eff, "TESS")
            self.assertEqual(exp_coeffs, coeffs,
                             f"Kepler pow2 coeffs {coeffs} mismatch data file ln {exp_coeffs_line}")

    def test_lookup_pow2_ld_coeffs_kepler_basic(self):
        """ Tests lookup_pow2_coefficients(logg, t_eff, "Kepler") """
        reference_data = limb_darkening._pow2_ld_coeffs_table("Kepler")
        for (logg,  t_eff,      exp_coeffs_line) in [
            # Test finding correct data in the range where logg steps are 0.5 and teff are 100 K
            (4.0,   6500.0,     self.pow2_line_4_0_6500),
            (4.24,  6500.0,     self.pow2_line_4_0_6500),
            (3.76,  6500.0,     self.pow2_line_4_0_6500),
            (4.0,   6549.9,     self.pow2_line_4_0_6500),
            (4.0,   6450.1,     self.pow2_line_4_0_6500),

            # These test the region where the temp steps change from 100 to 200 K (temps >=7000).
            # They're expected to return the values for logg 4.0, T_eff 7200 (no 7100, 7300 rows).
            (4.0,   7100.1,     self.pow2_line_4_0_7200),
            (4.0,   7299.0,     self.pow2_line_4_0_7200),

            # There's a gap in the coeffs between Teff 4900 and 5100 K
            # Test the case where we need to round away from 5000, otherwise we get a KeyError.
            (4.81,  4956.7,     self.pow2_line_5_0_4900),
            (5.24,  5021.3,     self.pow2_line_5_0_5100),

            # The logg covers [0.0, 6.0] and Teff [2300, 12000] K
            # Test the cases where request outside this range -> expect to use limts
            (0.0,   2300.0,     self.pow2_line_min_2300),
            (6.5,   12000.0,    self.pow2_line_max_12000),
            (4.0,   2000.0,     self.pow2_line_4_0_min),
            (4.0,   12600.0,    self.pow2_line_4_0_max),
        ]:
            exp_coeffs = tuple(reference_data[exp_coeffs_line - 1][["g", "h"]])
            coeffs = limb_darkening.lookup_pow2_coefficients(logg, t_eff, "Kepler")
            self.assertEqual(exp_coeffs, coeffs,
                             f"Kepler pow2 coeffs {coeffs} mismatch data file ln {exp_coeffs_line}")

if __name__ == "__main__":
    unittest.main()
