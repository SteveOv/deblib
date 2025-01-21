""" Unit tests for the jktebop module. """
import os
import unittest
import inspect

from io import StringIO
from pathlib import Path
from subprocess import CalledProcessError
from string import Template

import numpy as np

from deblib.jktebop import jktebop

class Testjktebop(unittest.TestCase):
    """ Unit tests for the jktebop module. """
    _jktebop_dir = Path(os.environ.get("JKTEBOP_DIR", "~/jktebop/")).expanduser().absolute()

    _task2_in_template = """2       5       Task to do (from 2 to 9)   Integ. ring size (deg)
0.3     0.5     Sum of fractional radii    Ratio of the radii
${inc}  0.5     Orbital inclination (deg)  Mass ratio of system
0.0     0.0     ecosw or eccentricity      esinw or periastron long
0.0     0.0     Gravity darkening (star A) Grav darkening (star B)
0.8     0.0     Surface brightness ratio   Amount of third light 
quad    quad    LD law type for star A     LD law type for star B
0.25    0.25    LD star A (coeff 1)        LD star B (coeff 1)
0.22    0.22    LD star A (coeff 2)        LD star B (coeff 2)
0.0     0.0     Reflection effect star A   Reflection effect star B
0.0     0.0     Phase of primary eclipse   Light scale factor (mag)
${out_filename}
"""

    #
    # Tests execute_task(in_filename, out_filename, cleanup_pattern, raise_warnings, stdout_to)
    #
    def test_execute_task_valid(self):
        """ Test execute_task(all params for full task 2 happy path) check all processing """
        # Clear out any artefacts from previous run of this test & generate a new valid in file
        in_file, out_file = self._test_specific_in_and_out_filenames(unlink_existing=True)
        self._write_task2_in_file(in_file, out_file=out_file)
        cleanup_pattern = f"{in_file.stem}.*"
        stdout_to = StringIO()

        # Run the task and capture the response in a list[str]
        out_lines = list(jktebop.execute_task(in_file, out_file, cleanup_pattern, True, stdout_to))

        # Assert processing
        model = np.loadtxt(out_lines, comments="#", dtype=np.double, unpack=True)
        self.assertEqual(model.shape[0], 5)                     # out file of 5 columns & many rows
        self.assertTrue(model.shape[1] > 0)
        self.assertFalse(in_file.exists())                      # working files cleaned up
        self.assertFalse(out_file.exists())
        self.assertNotIn("### ERROR", stdout_to.getvalue())     # no errors written to stdout

    def test_execute_task_valid_no_cleanup(self):
        """ Test execute_task(happy path, but no cleanup_pattern) check in/out files left behind """
        # Clear out any artefacts from previous run of this test & generate a new valid in file
        in_file, out_file = self._test_specific_in_and_out_filenames(unlink_existing=True)
        self._write_task2_in_file(in_file, out_file=out_file)

        # Run the task and wait for completion (based on the generator terminating)
        list(jktebop.execute_task(in_file, out_file, None))

        # Assert in and out files not cleaned down
        self.assertTrue(in_file.exists())
        self.assertTrue(out_file.exists())

    def test_execute_task_valid_test_stdout_to(self):
        """ Test execute_task(happy path specifically testing stdout_to) """
        # Clear out any artefacts from previous run of this test & generate a new valid in file
        in_file, out_file = self._test_specific_in_and_out_filenames(unlink_existing=True)
        self._write_task2_in_file(in_file, out_file=out_file)
        cleanup_pattern = f"{in_file.stem}.*"
        stdout_to = StringIO()

        # Run the task and wait for completion (based on the generator terminating)
        list(jktebop.execute_task(in_file, out_file, cleanup_pattern, stdout_to=stdout_to))

        # Look for text indicating that the processing has worked through successfully
        console_text = stdout_to.getvalue()
        self.assertIn(f"Opened new lightcurve file:  {out_file.name}", console_text)

    def test_execute_task_invalid_inc_value(self):
        """ Test execute_task(in_file has invalid inc value) so raises CalledProcessError """
        # Clear artefacts from previous run of this test & generate a new in file with invalid inc
        in_file, out_file = self._test_specific_in_and_out_filenames(unlink_existing=True)
        self._write_task2_in_file(in_file, inc=45.0, out_file=out_file) # range for inc (50, 140)
        cleanup_pattern = f"{in_file.stem}.*"

        # Assert we get an error and the output contains text indicating what the problem may be
        with self.assertRaises(CalledProcessError) as ect:
            list(jktebop.execute_task(in_file, out_file, cleanup_pattern))
        self.assertIn("### ERROR: the value of INCLNATION", ect.exception.output)

    def test_execute_task_missing_in_file(self):
        """ Test execute_task(in_file has invalid inc value) so raises CalledProcessError """
        # Clear artefacts with these names but do not generate anything
        in_file, out_file = self._test_specific_in_and_out_filenames(unlink_existing=True)
        with self.assertRaises(FileNotFoundError):
            list(jktebop.execute_task(in_file, out_file, None))


    #
    # Tests execute_task_async(in_filename) -> Popen[str]:
    #
    def test_execute_task_async_valid_in_file(self):
        """ Test execute_task_async(in_file is valid) returns valid Popen which can be waited on """
        in_file, out_file = self._test_specific_in_and_out_filenames(unlink_existing=True)
        self._write_task2_in_file(in_file, out_file=out_file)

        with jktebop.execute_task_async(in_file) as proc:
            self.assertIsNone(proc.poll())  # Will return None if still running
            proc.wait()

    def test_execute_task_async_missing_in_file(self):
        """ Test execute_task_async(in_file is mission) so raises FileNotFoundError """
        # Clear artefacts with these names but do not generate anything
        in_file, _ = self._test_specific_in_and_out_filenames(unlink_existing=True)
        with self.assertRaises(FileNotFoundError):
            jktebop.execute_task_async(in_file)



    # Helper functions
    def _test_specific_in_and_out_filenames(self, unlink_existing: bool=False):
        """ Generates matching in and out file names based on the calling function name """
        in_file = self._jktebop_dir / f"{inspect.stack()[1].function}.in"
        out_file = self._jktebop_dir / f"{in_file.stem}.out"
        if unlink_existing:
            for file in [in_file, out_file]:
                file.unlink(missing_ok=True)
        return (in_file, out_file)

    def _write_task2_in_file(self, filename: Path, out_file: Path, inc: float=90.0):
        template = Template(self._task2_in_template)
        with open(filename, "w", encoding="utf8") as of:
            of.write(template.substitute(inc=inc, out_filename=out_file.name))


if __name__ == '__main__':
    unittest.main()
