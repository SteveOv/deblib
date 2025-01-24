""" Classes for executing jktebop tasks with the aid of input file templates. """
# pylint: disable=no-name-in-module
from typing import Generator, Dict
from inspect import getsourcefile
from pathlib import Path
from tempfile import NamedTemporaryFile
from os import environ
from io import TextIOBase
from abc import ABC
from string import Template

import numpy as np

from .jktebop import execute_task
from .templateex import TemplateEx

# pylint: disable=too-many-arguments, dangerous-default-value

class Task(ABC):
    """ Base class for a jktebop task. """
    _this_dir = Path(getsourcefile(lambda:0)).parent
    _jktebop_dir = Path(environ.get("JKTEBOP_DIR", "~/jktebop/")).expanduser().absolute()

    def __init__(self, working_dir: Path, template: Template):
        """
        Initializes this Task which can execute jktebop tasks in the
        target_dir from input files generated from the task specific template

        :working_dir: the directory we will use for the task input and output files
        :template: the template for this task's input files
        """
        self._working_dir = working_dir
        self._template = template

        if isinstance(template, TemplateEx):
            self._default_params = template.get_identifiers_and_defaults()
        else:
            ids = TemplateEx.get_template_identifiers(template)
            self._default_params = { i: None for i in ids }
        super().__init__()

    @property
    def working_dir(self) -> Path:
        """ The working directory within which tasks will be executed. """
        return self._working_dir

    @property
    def template(self) -> Template:
        """ The template used to generate this task's input file. """
        return self._template

    @property
    def default_params(self) -> Dict[str, any]:
        """ The dictionary of the task's template params pre-populated with any default values """
        return self._default_params

    def run(self,
            params: Dict[str, any],
            file_stem: str,
            primary_result_file_ext: str=None,
            do_cleanup: bool=True,
            raise_warnings: bool=True,
            stdout_to: TextIOBase=None) -> Generator[str, None, None]:
        """
        Run this Task while redirecting jktebop console output to stdout_to.
        If primary_result_file_ext is given and the Task completes without
        error, the corresponding file will be opened and returned line by line.
        
        :params: the params dictionary to apply to this Task's template to generate the in file
        :file_stem: the stem of all files generated for this Task (in and output)
        :primary_result_file_ext: (optional) extension of the result file to open and read
        :do_cleanup: whether or not to remove the in and output files if no error raised
        :raise_warnings: whether or not to raise warnings from jktebop console warning output
        :stdout_to: (optional) target to write jktebop stdout + stderr output to
        """
        # Clean out existing jktebop files matching this stem; it'll fail if an output file exists
        self._cleanup_files(file_stem)

        in_file = self.working_dir / f"{file_stem}.in"
        if primary_result_file_ext:
            result_file = self.working_dir / f"{file_stem}.{primary_result_file_ext}"
        else:
            result_file = None

        self._write_in_file(in_file, params)
        execute_task(in_file, result_file, raise_warnings, stdout_to) # Blocking call

        if result_file:
            with open(result_file, mode="r", encoding="utf8") as of:
                yield from of

        if do_cleanup:
            self._cleanup_files(file_stem)

    def _write_in_file(self, filename: Path, params: Dict[str, any]):
        """ (over) write a jktebop .in file based on the Task's template and the given params """
        filename.write_text(self._template.substitute(params), encoding="utf8")

    def _cleanup_files(self, file_stem: str):
        """ Remove known jktebop filetypes within the working dir & matching the requested stem. """
        for ext in ["in", "par", "out", "fit"]:
            (self.working_dir / f"{file_stem}.{ext}").unlink(missing_ok=True)


class Task2(Task):
    """
    The jktebop task 2 which is used to generate model, phase-folded,
    light curves for given sets of parameters.
    """
    # Defines the "columns" of the structured array returned by generate_model_light_curve()
    _model_lc_dtype = np.dtype([("phase", float), ("delta_mag", float)])

    def __init__(self, working_dir: Path=Task._jktebop_dir):
        """
        Initializes this Task to execute jktebop #2 tasks in the working_dir
        from input files generated from the task specific template file
        ../data/jktebop/task2.in.templateex

        :working_dir: the directory we will use for the task input and output files
        """
        template_file = self._this_dir / "../data/jktebop/task2.in.templateex"
        template = TemplateEx(template_file.read_text("utf8"))
        super().__init__(working_dir, template)

    def run(self,
            params: Dict[str, any],
            file_stem: str,
            primary_result_file_ext: str="out",
            do_cleanup: bool=True,
            raise_warnings: bool=True,
            stdout_to: TextIOBase=None) -> Generator[str, None, None]:
        # pylint: disable=too-many-arguments
        # Create a unique temp .in file with equivalent output file so they're easy to clean up.
        # Leave deleting the temp file(s) to run() so they're retained if there's been an error.
        with NamedTemporaryFile(dir=self.working_dir, prefix=file_stem, suffix=".in",
                                delete=False, mode="w", encoding="utf8") as wf:
            in_file = Path(wf.name)
            (params := params or {})["out_file_name"] = f"{in_file.stem}.{primary_result_file_ext}"
            return super().run(params, in_file.stem, primary_result_file_ext,
                               do_cleanup, raise_warnings, stdout_to)

    def run_and_read_light_curve(self,
                                 params: Dict[str, any],
                                 file_prefix: str="task2-") -> np.ndarray[float]:
        """
        Wrapper function for running this Task to generate a model light curve
        for the passed set of the parameter values, returning the resulting data
        as a numpy structured array with named phase and delta_mag "columns"

        :params: the param values to be applied to this task's template - any
        existing out_file_name item will be overrwritten with a generated value
        :file_prefix: short prefix to apply to all in/out temp files generated
        :returns: a numpy structured array with named phase and delta_mag "columns"
        """
        return np.loadtxt(self.run(params, file_prefix), dtype=self._model_lc_dtype,
                          comments="#", usecols=(0, 1), unpack=False)
