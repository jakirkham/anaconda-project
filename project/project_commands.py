"""Class representing a command from the project file."""
from __future__ import absolute_import

from distutils.spawn import find_executable

import os


class ProjectCommand(object):
    """Represents an command from the project file."""

    def __init__(self, name, attributes):
        """Construct a command with the given attributes.

        Args:
            name (str): name of the command
            attributes (dict): named attributes of the command
        """
        self._name = name
        self._attributes = attributes.copy()

    @property
    def name(self):
        """Get name of the command."""
        return self._name

    def launch_argv_for_environment(self, environ):
        """Get a usable argv with the executable path made absolute and prefix substituted.

        Args:
            environ (dict): the environment
        Returns:
            argv as list of strings
        """
        for name in ('CONDA_ENV_PATH', 'PATH', 'PROJECT_DIR'):
            if name not in environ:
                raise ValueError("To get a runnable command for the app, %s must be set." % (name))

        args = None

        # see conda.misc::launch for what we're copying
        app_entry = self._attributes.get('conda_app_entry', None)
        if app_entry is not None:
            # conda.misc uses plain split and not shlex or
            # anything like that, we need to match its
            # interpretation
            parsed = app_entry.split()
            args = []
            for arg in parsed:
                if '${PREFIX}' in arg:
                    arg = arg.replace('${PREFIX}', environ['CONDA_ENV_PATH'])
                args.append(arg)

        # this should have been validated when loading the project file
        assert args is not None

        # always look in the project directory. This is a little
        # odd because we don't add PROJECT_DIR to PATH for child
        # processes - maybe we should?
        path = os.pathsep.join([environ['PROJECT_DIR'], environ['PATH']])
        executable = find_executable(args[0], path)
        if executable is not None:
            # if the executable is in cwd, for some reason find_executable does not
            # return the full path to it, just a relative path.
            args[0] = os.path.abspath(executable)
        # if we didn't find args[0] on the path, we leave it as-is
        # and wait for it to fail when we later try to run it.
        return args