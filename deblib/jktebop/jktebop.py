""" Low-level module for invoking the JKTEBOP dEB light curve fitting code. """
from typing import Generator
from subprocess import Popen, PIPE, STDOUT, CalledProcessError
from threading import Thread
from io import TextIOBase, StringIO
from pathlib import Path
import warnings


class JktebopWarning(UserWarning):
    """ A Base Warning specific to JKTEBOP. """

# class JktebopParameterWarning(JktebopWarning):
#     """ A warning arising from JKTEBOP input parameter """

class JktebopTaskWarning(JktebopWarning):
    """ A warning arising from JKTEBOP task processing """


class PassThroughStringIO(StringIO):
    """
    StringIO which allows interception of writes while passing through to an optional 2nd instance.
    """
    def __init__(self, pass_to: TextIOBase=None):
        self._pass_to = pass_to
        super().__init__()

    def write(self, s):
        if self._pass_to:
            self._pass_to.write(s)
        return super().write(s)

    def writelines(self, lines):
        if self._pass_to:
            self._pass_to.writelines(lines)
        return super().writelines(lines)


def execute_task(in_file: Path,
                 out_file: Path=None,
                 cleanup_pattern: str=None,
                 raise_warnings: bool=False,
                 stdout_to: TextIOBase=None) -> Generator[str, None, None]:
    """
    Will run JKTEBOP against the passed in file, waiting for the production of the
    expected out file. The contents of the outfile will be yielded line by line.

    The function returns a Generator[str] yielding the lines of text written to
    the out_filename. These can be read in a for loop:
    ```Python
    for line in execute_task(...):
        ...
    ```
    or, to capture everything wrap it in a list() function:
    ```Python
    lines = list(execute_task(...))
    ```

    To redirect the stdout/stderr output from JKTEBOP set stdout_to to an
    instance of a TextIOBase, for example:
    ```Python
    execute_task(..., stdout_to=sys.stdout)
    ```

    :in_file: the Path of the in file containing the JKTEBOP input parameters.
    This should be in a directory where jktebop executable is visible.
    :out_file: optional the Path of the primary output file we expect be created.
    If given, the file will be read with its contents yielded line by line with a Generator.
    :cleanup_pattern: optional glob pattern of files, within the working dir, to be deleted after
    successful processing. The files will not be deleted if there is a failure.
    :raise_warnings: if True, raise warnings for any warning text in the output
    :stdout_to: if given, the JKTEBOP stdout/stderr will be redirected here
    :returns: yields the content of the primary output file, line by line.
    """
    # pylint: disable=too-many-locals
    # Internal capture and forward of the process console output for reporting on error conditions
    my_stdout_to = PassThroughStringIO(stdout_to)

    # Call out to jktebop to process the in file and generate the requested output file
    return_code = 0
    cmd = ["./jktebop", f"{in_file.name}"]
    with execute_task_async(in_file) as proc:
        # We're using an async call so we can redirect anything written to stdout/stderr to the
        # requested TextIOBase instance as they happen using the following on a new thread.
        def capture_process_stdout():
            while True:
                # Await the command's next output - we'll get None/empty if we've reached the end
                line = proc.stdout.readline()
                if not line:
                    break

                my_stdout_to.write(line)
                if raise_warnings and "warning" in line.casefold():
                    warnings.warn(message=line, category=JktebopTaskWarning)

        stdout_thread = Thread(target=capture_process_stdout)
        stdout_thread.start()

        return_code = proc.wait()
        stdout_thread.join()

    # "Returned" from the subprocess so first check for any indication of failure
    output = my_stdout_to.getvalue()
    if return_code != 0 or not out_file.exists() or "### ERROR" in output:
        # JKTEBOP (v43) doesn't appear to set the response code on a failure so
        # we also use the absence of the output file or console text to indicate a problem
        raise CalledProcessError(return_code, cmd=cmd, output=output)

    # Yield the contents of the output file
    if out_file:
        with open(out_file, mode="r", encoding="utf8") as of:
            yield from of

    # Optional cleanup
    if cleanup_pattern:
        for parent in [in_file.parent, out_file.parent]:
            for file in parent.glob(cleanup_pattern):
                file.unlink()


def execute_task_async(in_file: Path) -> Popen[str]:
    """
    Will execute jktebop against the passed in file asynchronously and return immediately.
    Assumes that the jktebop executable is visible within/to the in_file directory.

    Suggested use:
    ```python
    with execute_task_async(in_file=in_file) as proc:
        # ...
        return_code = proc.wait()
    ```

    :in_file: the path/file name of the in file containing the jktebop input parameters
    :returns: a Popen[str] instance allowing communication/wait on the subprocess
    """
    # pylint: disable=consider-using-with
    if not in_file.exists():
        raise FileNotFoundError(in_file)

    # Call out to jktebop to process the in file and generate the requested output file
    cmd = ["./jktebop", f"{in_file.name}"]
    working_dir = in_file.parent
    return Popen(cmd, cwd=working_dir, stdout=PIPE, stderr=STDOUT, text=True)
