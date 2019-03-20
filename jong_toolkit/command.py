# coding: utf-8
# python lib
import configparser
import os
from pathlib import Path
import shlex
import subprocess
import itertools

cwd = Path.cwd()

config = configparser.ConfigParser()
config.read(str(cwd) + '/jong_toolkit/settings.ini')

class JongToolKitCommand:

    def _command(self, file):
        """
        command to build
        :param file: file to import
        :return: built command
        """
        command = config['JOPLIN_CONFIG']['JOPLIN_BIN_PATH']

        if config['JOPLIN_CONFIG']['JOPLIN_PROFILE_PATH']:
            command += ' --profile {} '.format(config['JOPLIN_CONFIG']['JOPLIN_PROFILE_PATH'])

        command += ' import {} {}'.format(file, config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_FOLDER'])
        return command

    def _joplin_run(self, file):
        """
        command to run
        :param file: the file to import
        """

        args = shlex.split(self._command(file))

        result = subprocess.run(args)

        if result.returncode == 0:
            os.unlink(file)


