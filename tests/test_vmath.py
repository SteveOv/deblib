""" Unit tests for the vmath module. """
from typing import List, Tuple
import unittest

import math
import numpy as np

# pylint: disable=no-member
from uncertainties import ufloat, UFloat, umath

from deblib import vmath

class Testvmath(unittest.TestCase):
    """ Unit tests for the stellar module. """
    # pylint: disable=too-many-public-methods, line-too-long

    def test_degrees_calculations(self):
        """ Basic suite of tests for the degrees function calculations """
        self.__test_calcs(vmath.degrees, [(0, 0), (1, 0), (0.75, 0.01), (-0.63, 0.1)])

    def test_radians_calculations(self):
        """ Basic suite of tests for the radians function calculations """
        self.__test_calcs(vmath.radians, [(0, 0), (90, 0), (230, 0), (34.5, 0.01), (73.1, 0.4), (-50., 0.4)])

    def test_sin_calculations(self):
        """ Basic suite of tests for the sin function calculations """
        self.__test_calcs(vmath.sin, [(0, 0), (1, 0), (0.75, 0.01), (-0.63, 0.1)])

    def test_cos_calculations(self):
        """ Basic suite of tests for the cos function calculations """
        self.__test_calcs(vmath.cos, [(0, 0), (1, 0), (0.75, 0.01), (-0.63, 0.1)])

    def test_tan_calculations(self):
        """ Basic suite of tests for the tan function calculations """
        self.__test_calcs(vmath.tan, [(0, 0), (1, 0), (0.12, 0.01), (-0.18, 0.1)])

    def test_asin_calculations(self):
        """ Basic suite of tests for the acos function calculations """
        self.__test_calcs(vmath.asin, [(0, 0), (0.99, 0), (0.75, 0.01), (-0.63, 0.1)])

    def test_acos_calculations(self):
        """ Basic suite of tests for the acos function calculations """
        self.__test_calcs(vmath.acos, [(0, 0), (0.99, 0), (0.75, 0.01), (-0.63, 0.1)])

    def test_atan_calculations(self):
        """ Basic suite of tests for the atan function calculations """
        self.__test_calcs(vmath.atan, [(0, 0), (0.99, 0), (0.75, 0.01), (-0.63, 0.1)])

    def test_exp_calculations(self):
        """ Basic suite of tests for the exp function calculations """
        self.__test_calcs(vmath.exp, [(0, 0), (2.0, 0), (0.5, 0.01), (13.5, 0.21), (-0.75, 0.1)])

    def test_log10_calculations(self):
        """ Basic suite of tests for the exp function calculations """
        self.__test_calcs(vmath.log10, [(0.001, 0), (0.5, 0.01), (1.66, 0.121), (10.54, 0.5)])


    # pylint: disable=too-many-locals
    def __test_calcs(self, vmath_func, list_of_num_unc_vals: List[Tuple[float, float]]):
        """ Basic happy path tests of degrees() to assert correct results """
        numpy_names = {  # for when numpy uses a different func name
            "asin": "arcsin",
            "acos": "arccos",
            "atan": "arctan"
        }

        func_name = vmath_func.__name__
        math_func = getattr(math, func_name)
        numpy_func = getattr(np, numpy_names.get(func_name, func_name))
        umath_func = getattr(umath, func_name)

        # pylint: disable=too-many-arguments, too-many-locals
        def assert_result(self, x, expected, actual, ix: int=None):
            """ General assertEqual which handles UFloats """
            msg = f"vmath.{func_name}({x})" + (f"[{ix}]" if ix is not None else "")
            if isinstance(expected, UFloat):
                self.assertIsInstance(actual, UFloat, msg + f": {actual} expected to be a UFloat")
                for (lbl, exp, act) in [("n", expected.n, actual.n), ("s", expected.s, actual.s)]:
                    self.assertAlmostEqual(exp, act, 12, msg + f".{lbl}: actual {act} != expected {exp}")
            else:
                self.assertAlmostEqual(expected, actual, 12, msg + f": {actual} != expected {expected}")

        for (nom, unc) in list_of_num_unc_vals:
            # Calculate the expected value from the appropriate reference function
            for (x,                                 expected) in [
                (nom,                               math_func(nom)),
                ([nom]*2,                           numpy_func([nom]*2)),
                (np.array([nom]*2),                 numpy_func(np.array([nom]*2))),
                (ufloat(nom, unc),                  umath_func(ufloat(nom, unc))),
                (np.array([ufloat(nom, unc)]*2),    np.array([umath_func(x) for x in [ufloat(nom, unc)]]*2)),
            ]:
                actual = vmath_func(x)
                if isinstance(expected, np.ndarray):
                    msg = f"{func_name}({x})=={actual}"
                    self.assertIsInstance(actual, np.ndarray, msg + ": output not ndarray")
                    self.assertEqual(len(expected), len(actual), msg + ": input/output lengths differ")
                    for (ix, (x, exp, act)) in enumerate(zip(x, expected, actual)):
                        assert_result(self, x, exp, act, ix)
                else:
                    assert_result(self, nom, expected, actual)


if __name__ == "__main__":
    unittest.main()
