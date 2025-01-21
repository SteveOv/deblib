""" Unit tests for the task module/classes. """
import unittest
from pathlib import Path
from os import environ

from deblib.jktebop.task import Task2

class Testjktebop(unittest.TestCase):
    """ Unit tests for the task module/classes. """
    _jktebop_dir = Path(environ.get("JKTEBOP_DIR", "~/jktebop/")).expanduser().absolute()

    #
    # class: Task2
    #
    def test_class2_generate_model_light_curve_happy_path(self):
        """ Test Task2.generate_model_light_curve(happy path) """
        task = Task2(self._jktebop_dir)

        params = {
            **task.get_default_params(),
            "sumr": 0.3,    "k": 0.5,
            "inc": 90,      "qphot": 1,
            "J": 0.5,       "L3": 0,
            "LDA": "quad",  "LDB": "quad",
            "LDA1": 0.25,   "LDB1": 0.25,
            "LDA2": 0.23,   "LDB2": 0.23,
        }

        model = task.generate_model_light_curve(**params)
        self.assertTrue(model.shape[0] > 1000)  # it's usually 10001
        self.assertIn("phase", model.dtype.names)
        self.assertIn("delta_mag", model.dtype.names)


if __name__ == '__main__':
    unittest.main()
