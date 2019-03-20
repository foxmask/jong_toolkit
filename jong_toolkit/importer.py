# coding: utf-8
# python lib
import configparser
from pathlib import Path
import itertools

from command import JongToolKitCommand

"""
    JongToolKitImporter:
    ====================
    
    Use it to import file in markdown from the cloud storage service

    example: 

    >>> from jong_toolkit.go import go
    >>> go()
    
    or  

    >>> from jong_toolkit.go import JongToolKitImporter
    >>> file = '/somewhere/Dropbox/Applications/Joplin/letterbox/foorbar.md'
    >>> jtki = JongToolKitImporter()
    >>> jtki.import_note(file)

"""
cwd = Path.cwd()

config = configparser.ConfigParser()
config.read(str(cwd) + '/jong_toolkit/settings.ini')


class JongToolKitImporter(JongToolKitCommand):
    """
    Jong Importer class to deal with markdown files located on the cloud storage service to import in Joplin
    """

    def import_note(self, file):
        """
        importing a file
        :param file: file to import
        """
        self._joplin_run(file)


def go():
    """
    read the folder of the file to import
    """

    jtki = JongToolKitImporter()
    md_files = Path(config['JOPLIN_CONFIG']['JOPLIN_IMPORT_FOLDER']).glob('*.md')
    jex_files = Path(config['JOPLIN_CONFIG']['JOPLIN_IMPORT_FOLDER']).glob('*.jex')
    # concatenate the 2 generators
    files = itertools.chain(md_files, jex_files)
    # read the files to import
    for file in files:
        jtki.import_note(file)


if __name__ == '__main__':
    go()
