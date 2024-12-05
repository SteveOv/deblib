""" Unit tests for the stellar module. """
import unittest
import numpy as np

from deblib.stellar import log_g
from deblib.constants import M_sun, R_sun

class Teststellar(unittest.TestCase):
    """ Unit tests for the stellar module. """
    # pylint: disable=too-many-public-methods, line-too-long

    #
    # Test log_g(mass, radius)
    #
    def test_log_g_base(self):
        """ Basic happy path tests of log_g() to assert handling of args """
        for (m,                                 r,                                  exp_logg) in [
            # M_SUN and R_SUN are already UFloats
            (M_sun.nominal_value,               R_sun.nominal_value,                4.4),
            (M_sun,                             R_sun,                              4.4),
            (np.array([M_sun.nominal_value]*9), np.array([R_sun.nominal_value]*9),  np.array([4.4]*9)),
            (np.array([M_sun]*9),               np.array([R_sun]*9),                np.array([4.4]*9)),
        ]:
            logg = log_g(m, r)
            for expected, actual in zip(exp_logg if isinstance(exp_logg, np.ndarray) else np.array([exp_logg]),
                                    logg if isinstance(logg, np.ndarray) else np.array([logg])):
                self.assertAlmostEqual(expected, actual.nominal_value, 1)

if __name__ == "__main__":
    unittest.main()
