""" Low-level module for invoking the JKTEBOP dEB light curve fitting code. """
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
                 out_file: Path,
                 raise_warnings: bool=False,
                 stdout_to: TextIOBase=None):
    """
    Will run JKTEBOP against the passed in file and wait for completion.

    :in_file: the Path of the in file containing the JKTEBOP input parameters.
    This should be in a directory where jktebop executable is visible.
    :out_file: optional the Path of the primary output file we expect be created.
    If given and missing will be seen as evidence that the task was not successful.
    :raise_warnings: if True, raise warnings for any warning text in the output
    :stdout_to: if given, the JKTEBOP stdout/stderr will be redirected here
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
    if return_code != 0 or "### ERROR" in output or (out_file and not out_file.exists()):
        # JKTEBOP (v43) doesn't appear to set the response code on a failure so we
        # also use the console text or absence of the output file to indicate a problem
        raise CalledProcessError(return_code, cmd=cmd, output=output)


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
    if not in_file.exists():
        raise FileNotFoundError(in_file)

    cmd = ["./jktebop", f"{in_file.name}"]
    working_dir = in_file.parent

    # Call out to jktebop to process the in file and generate the requested output file
    # pylint: disable=consider-using-with
    return Popen(cmd, cwd=working_dir, stdout=PIPE, stderr=STDOUT, text=True)
