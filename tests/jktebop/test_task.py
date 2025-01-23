""" Unit tests for the task module/classes. """
# pylint: disable=protected-access
import unittest
from pathlib import Path
from os import environ
from string import Template
from subprocess import CalledProcessError

from deblib.jktebop.task import Task, Task2
from deblib.jktebop.templateex import TemplateEx

class TaskTestSubclass(Task):
    """ A subclass of Task used for testing. """

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
        self.assertEqual({}, task.default_params)

    def test_task_init_with_template_check_params(self):
        """ Test Task.get_default_params(Template) publishes all tokens in template """
        task = TaskTestSubclass(self._jktebop_dir, Template(r"${t1} ${t2} t3"))
        self.assertIn("t1", task.default_params, "expect to find t1 param")
        self.assertIsNone(task.default_params["t1"], "expect t1==None")
        self.assertIn("t2", task.default_params, "expect to find t2 param")
        self.assertIsNone(task.default_params["t2"], "expect t2==None")
        self.assertNotIn("t3", task.default_params, "not expected to find t3 param")

    def test_task_init_with_templateex_check_params(self):
        """ Test Task.get_default_params(TemplateEx) publishes all tokens|defaults in template """
        task = TaskTestSubclass(self._jktebop_dir, TemplateEx(r"${t1|1.0} ${tnone} ${tempty|} t4"))
        self.assertIn("t1", task.default_params, "expect to find t1 param")
        self.assertEqual("1.0", task.default_params["t1"], "expect t1=='1.0'")
        self.assertIn("tnone", task.default_params, "expect to find tnone param")
        self.assertIsNone(task.default_params["tnone"], "expect tnone==None")
        self.assertIn("tempty", task.default_params, "expect to find tempty param")
        self.assertEqual("", task.default_params["tempty"], "expect tempty==''")
        self.assertNotIn("t4", task.default_params, "not expected to find t4 param")

    def test_task_write_in_file_happy_path(self):
        """ Test Task.write_in_file() > file is written with token substitutions """
        in_file = self._jktebop_dir / "test_task_write_in_file_happy_path.in"
        task = TaskTestSubclass(self._jktebop_dir, Template("${t1} ${t2} t3"))
        params = { "t1": "#1", "t2": "#2", "t3": "#3" }
        task.write_in_file(in_file, params)

        self.assertTrue(in_file.exists())
        in_file_text = in_file.read_text(encoding="utf8")
        self.assertIn("#1", in_file_text, "expect to find #1 (t1) in in_file")
        self.assertIn("#2", in_file_text, "expect to find #2 (t2) in in_file")
        # t3 not in template & we expect t3 param to be ignored (no error)
        self.assertNotIn("#3", in_file_text, "not expected to find #3 (t3) in in_file")

        self.addCleanup(self.remove_file, in_file)

    def test_task_write_in_file_missing_param(self):
        """ Test Task.write_in_file(missing param) > KeyError """
        in_file = self._jktebop_dir / "test_task_write_in_file_missing_param.in"
        in_file.unlink(missing_ok=True)
        task = TaskTestSubclass(self._jktebop_dir, Template("${t1} ${t2} t3"))
        with self.assertRaises(KeyError) as ect:
            params = {"t2": "#2", "t3": "#3"}
            task.write_in_file(in_file, params)
            self.assertIn("t1", ect.exception.output)
        self.assertFalse(in_file.exists())

        self.addCleanup(self.remove_file, in_file)

    #
    # class: Task2(Task)
    #
    def test_task2_generate_model_light_curve_happy_path(self):
        """ Test Task2.generate_model_light_curve(happy path) """
        task = Task2(self._jktebop_dir)

        # We don't need to pass in anything for those params where the default is to be used
        params = {
            # These don't have defaults and must be set
            "sumr": 0.3,    "k": 0.5,
            "inc": 90,
            "J": 0.5,
            "ecosw": 0.0,   "esinw": 0.0
        }

        # Will generate an in file with unique temp name, run the task, parse the primary output
        model = task.generate_model_light_curve(params, "test_task2_happy_path_")

        self.assertTrue(model.shape[0] > 1000)  # it's usually 10001
        self.assertIn("phase", model.dtype.names)
        self.assertIn("delta_mag", model.dtype.names)

    def test_task2_generate_model_light_curve_invalid_param_value(self):
        """ Test Task2.generate_model_light_curve() LDA invalid -> expect error """
        task = Task2(self._jktebop_dir)
        file_prefix = "test_task2_invalid_param_value_"

        params = {
            "sumr": 0.3,    "k": 0.5,
            "inc": "HELLO!", # <-- not a valid value
            "J": 0.5,
            "ecosw": 0.0,   "esinw": 0.0,
        }

        with self.assertRaises(CalledProcessError) as ect:
            task.generate_model_light_curve(params, file_prefix)
        self.assertIn("ERROR reading the parameters INCLNATION", ect.exception.output)

        for in_file in self._jktebop_dir.glob(f"{file_prefix}*.in"):
            self.addCleanup(self.remove_file, in_file)


    # Helpers
    def remove_file(self, file: Path):
        """ Will remove the indicated file if it exists. """
        file.unlink(missing_ok=True)


if __name__ == '__main__':
    unittest.main()
