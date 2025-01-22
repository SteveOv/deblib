""" Unit tests for the task module/classes. """
# pylint: disable=protected-access
import unittest
from pathlib import Path
from os import environ
from string import Template
from subprocess import CalledProcessError

from deblib.jktebop.task import Task, Task2

class TaskTestSubclass(Task):
    """ A subclass of Task used for testing. """
    def get_default_params(self, **overrides):
        return { **self._template_required_params.copy() }

class TestTask(unittest.TestCase):
    """ Unit tests for the task module/classes. """
    _jktebop_dir = Path(environ.get("JKTEBOP_DIR", "~/jktebop/")).expanduser().absolute()

    #
    # class: Task(ABC)
    #
    def test_task_init_happy_path(self):
        """ Test Task.__init__(happy path) """
        template = Template("")
        task = TaskTestSubclass(self._jktebop_dir, template)
        self.assertEqual(task.working_dir, self._jktebop_dir)
        self.assertEqual(task._template, template)
        self.assertEqual({}, task.get_default_params())

    def test_task_get_default_params_happy_path(self):
        """ Test Task.get_default_params() publishes all tokens in template """
        task = TaskTestSubclass(self._jktebop_dir, Template("${t1} ${t2} t3"))
        self.assertIn("t1", task.get_default_params(), "expect to find t1 param")
        self.assertIn("t2", task.get_default_params(), "expect to find t2 param")
        self.assertNotIn("t3", task.get_default_params(), "not expected to find t3 param")

    def test_task_write_in_file_happy_path(self):
        """ Test Task.write_in_file() > file is written with token substitutions """
        in_file = self._jktebop_dir / "test_task_in_file.in"
        task = TaskTestSubclass(self._jktebop_dir, Template("${t1} ${t2} t3"))
        task.write_in_file(in_file, t1="#1", t2="#2", t3="#3")

        self.assertTrue(in_file.exists())
        in_file_text = in_file.read_text(encoding="utf8")
        self.assertIn("#1", in_file_text, "expect to find #1 (t1) in in_file")
        self.assertIn("#2", in_file_text, "expect to find #2 (t2) in in_file")
        # t3 not in template & we expect t3 param to be ignored (no error)
        self.assertNotIn("#3", in_file_text, "not expected to find #3 (t3) in in_file")
        in_file.unlink(missing_ok=True)

    def test_task_write_in_file_missing_param(self):
        """ Test Task.write_in_file(happy path) """
        in_file = self._jktebop_dir / "test_task_in_file.in"
        in_file.unlink(missing_ok=True)
        task = TaskTestSubclass(self._jktebop_dir, Template("${t1} ${t2} t3"))
        with self.assertRaises(KeyError) as ect:
            task.write_in_file(in_file, t2="#2", t3="#3")
            self.assertIn("t1", ect.exception.output)
        self.assertFalse(in_file.exists())

    #
    # class: Task2(Task)
    #
    def test_task2_generate_model_light_curve_happy_path(self):
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

        # Will generate an in file with unique temp name, run the task, parse the primary output
        model = task.generate_model_light_curve(**params)

        self.assertTrue(model.shape[0] > 1000)  # it's usually 10001
        self.assertIn("phase", model.dtype.names)
        self.assertIn("delta_mag", model.dtype.names)

    def test_task2_generate_model_light_curve_invalid_param_value(self):
        """ Test Task2.generate_model_light_curve() LDA invalid -> expect error """
        task = Task2(self._jktebop_dir)

        params = {
            **task.get_default_params(),
            "sumr": 0.3,    "k": 0.5,
            "inc": 90,      "qphot": 1,
            "J": 0.5,       "L3": 0,
            "LDA": "HELLO", "LDB": "quad",
            "LDA1": 0.25,   "LDB1": 0.25,
            "LDA2": 0.23,   "LDB2": 0.23,
        }

        with self.assertRaises(CalledProcessError) as ect:
            task.generate_model_light_curve(**params)
            self.assertIn("ERROR: limb darkening law for star A", ect.exception.output)

if __name__ == '__main__':
    unittest.main()
