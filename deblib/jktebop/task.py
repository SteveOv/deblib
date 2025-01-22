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
    def default_params(self) -> Dict[str, any]:
        """
        Returns the dictionary of the task's template params pre-populated with any default values
        """
        return self._default_params

    def write_in_file(self, filename: Path, **params):
        """
        Will (over) write a task in file based on the task's template and the given params
    
        :filename: the name of the file to write
        :params: the set of params to substitute into the task's template
        """
        filename.write_text(self._template.substitute(**params))

    def _run(self,
             in_file: Path,
             out_file: Path=None,
             raise_warnings: bool=False,
             stdout_to: TextIOBase=None):
        """
        Run this task and redirect its output. With this function we do not perform any cleanup
        or parse any files. Output files are left available for subsequent parsing.

        :in_file: the Path of the in file containing the JKTEBOP input parameters.
        This should be in a directory where jktebop executable is visible.
        :out_file: an output file we expect to be created - used as evidence of success
        :raise_warnings: whether to echo jktebop warning console text as python warnings
        :stdout_to: if given, the JKTEBOP stdout/stderr will be redirected here
        :returns: this instance (useful for chaining calls)
        """
        if out_file:
            out_file.unlink(missing_ok=True)
        execute_task(in_file, out_file, raise_warnings, stdout_to)
        return self

    def _run_and_yield_output(self,
                              in_file: Path,
                              out_file: Path=None,
                              cleanup_pattern: str=None,
                              raise_warnings: bool=False,
                              stdout_to: TextIOBase=None) -> Generator[str, None, None]:
        """
        Shortcut method for invoking this task, redirecting its output,
        performing cleanup and returning the content of the selected out file.
        """
        # pylint: disable=too-many-arguments
        self._run(in_file, out_file, raise_warnings, stdout_to)

        # Yield the contents of the output file
        if out_file:
            with open(out_file, mode="r", encoding="utf8") as of:
                yield from of

        # Optional cleanup
        if cleanup_pattern:
            for parent in [in_file.parent, out_file.parent]:
                for file in parent.glob(cleanup_pattern):
                    file.unlink()

class Task2(Task):
    """
    The jktebop task 2 which is used to generate model, phase-folded,
    light curves for given sets of parameters.
    """
    # Defines the "columns" of the structured array returned by generate_model_light_curve()
    _task2_model_dtype = np.dtype([("phase", float), ("delta_mag", float)])

    def __init__(self, working_dir: Path=Task._jktebop_dir):
        """
        Initializes this Task which can execute jktebop #2 tasks in the
        target_dir from input files generated from the task specific template;

        ../data/jktebop/task2.in.template template file

        which specifies the format, placeholders for dynamic param values and,
        for some placeholders, a usable default value

        :working_dir: the directory we will use for the task input and output files
        """
        template_file = self._this_dir / "../data/jktebop/task2.in.templateex"
        template = TemplateEx(template_file.read_text("utf8"))
        super().__init__(working_dir, template)

    def generate_model_light_curve(self, file_prefix: str="task2-", **params) -> np.ndarray[float]:
        """
        Wrapper function for executing this tasks to generate a model light curve
        for the passed set of the parameter values. The param out_filename will
        be overwritten with a temp file value generated at runtime.

        :file_prefix: short prefix to apply to all temp files generated
        :params: the param values to be applied to this task's template
        :returns: a numpy structured array with named phase and delta_mag "columns"
        """
        # Create a unique temp .in file for jktebop to process. Set it to write to an output file
        # with an equivalent name so they're both easy to clean up. We don't set delete=True here
        # as we want our own code to do the clean up (or leave the files if there's been an error).
        with NamedTemporaryFile(dir=self.working_dir, prefix=file_prefix, suffix=".in",
                                delete=False, mode="w", encoding="utf8") as wf:
            in_file = Path(wf.name)
            out_file = in_file.parent / (in_file.stem + ".out")
            params["out_filename"] = out_file.name
            self.write_in_file(in_file, **params)

        lines = self._run_and_yield_output(in_file, out_file, cleanup_pattern=in_file.stem + ".*")
        return np.loadtxt(lines, self._task2_model_dtype, "#", usecols=(0, 1), unpack=False)
