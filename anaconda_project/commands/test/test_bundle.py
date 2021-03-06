# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# Copyright © 2016, Continuum Analytics, Inc. All rights reserved.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# ----------------------------------------------------------------------------
from __future__ import absolute_import, print_function

import os
import zipfile

from anaconda_project.commands.main import _parse_args_and_run_subcommand
from anaconda_project.internal.test.tmpfile_utils import (with_directory_contents,
                                                          with_directory_contents_completing_project_file)
from anaconda_project.project_file import DEFAULT_PROJECT_FILENAME


def test_archive_command_on_empty_project(capsys):
    def check(dirname):
        archivefile = os.path.join(dirname, "foo.zip")
        code = _parse_args_and_run_subcommand(['anaconda-project', 'archive', '--directory', dirname, archivefile])
        assert code == 1

        out, err = capsys.readouterr()
        assert "anaconda-project.yml does not exist.\nCan't create an archive.\n" == err
        assert '' == out

        assert not os.path.exists(os.path.join(dirname, DEFAULT_PROJECT_FILENAME))
        assert not os.path.exists(archivefile)

    with_directory_contents(dict(), check)


def test_archive_command_on_simple_project(capsys):
    def check(dirname):
        archivefile = os.path.join(dirname, "foo.zip")
        code = _parse_args_and_run_subcommand(['anaconda-project', 'archive', '--directory', dirname, archivefile])
        assert code == 0

        out, err = capsys.readouterr()
        assert ('  added %s\n  added %s\nCreated project archive %s\n' % (os.path.join(
            "some_name", DEFAULT_PROJECT_FILENAME), os.path.join("some_name", "foo.py"), archivefile)) == out

        with zipfile.ZipFile(archivefile, mode='r') as zf:
            assert [os.path.basename(x) for x in sorted(zf.namelist())] == [DEFAULT_PROJECT_FILENAME, "foo.py"]

        assert os.path.exists(os.path.join(dirname, DEFAULT_PROJECT_FILENAME))

        assert '' == err

    with_directory_contents_completing_project_file({'foo.py': 'print("hello")\n'}, check)


def test_archive_command_on_invalid_project(capsys):
    def check(dirname):
        code = _parse_args_and_run_subcommand(['anaconda-project', 'archive', '--directory', dirname, 'foo.zip'])
        assert code == 1

        out, err = capsys.readouterr()
        assert '' == out
        assert ('variables section contains wrong value type 42,' + ' should be dict or list of requirements\n' +
                'Unable to load the project.\n') in err

    with_directory_contents_completing_project_file({DEFAULT_PROJECT_FILENAME: "variables:\n  42"}, check)
