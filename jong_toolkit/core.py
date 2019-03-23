# coding: utf-8
# python lib
import configparser
import itertools
import os
from pathlib import Path
import shlex
import subprocess
from urllib.request import urlopen

# external lib
from joplin_api import JoplinApi
from bs4 import BeautifulSoup
import pypandoc

current_folder = os.path.dirname(__file__)
config = configparser.ConfigParser()
config.read(os.path.join(current_folder, 'settings.ini'))

joplin = JoplinApi(token=config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN'])


class JongToolKitCollector:
    """
        JongToolKitCollector:
        =====================

        Use it to collect shared notes, on your mobile, that just contain an URL as content
        then this will create a note for you from that URL

        example:

        >>> from jong_toolkit.jong_toolkit import JongToolKitCollector
        >>> jtkc = JongToolKitCollector()
        >>> jtkc.update_notes()
    """

    def get_tags_notes(self, tag):
        """
        get the note with the given tag

        :tag :string: the tag that will allow to find note with that tag
        :return json
        """
        return joplin.get_tags_notes(tag)

    def grab_note(self, note):
        """
        grab the webpage of that note
        :note :dict: dict of the shared note
        :return title of the grabed page and its body
        """
        # the body contains the URL all alone
        body = urlopen(note['body'])
        page = BeautifulSoup(body, 'html.parser')
        return page.title.string, page.body

    def update_notes(self):
        """
        create notes related to a given tag
        """
        joplin_tag = config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_TAG']
        tags = joplin.get_tags().json()
        for tag in tags:
            if tag['title'] == joplin_tag.lower():
                for note in self.get_tags_notes(tag['id']).json():
                    title, body = self.grab_note(note)
                    params = {'source_url': note['body']}
                    content = pypandoc.convert_text(body.decode(), config['JOPLIN_CONFIG']['PYPANDOC_MARKDOWN'], format='html')
                    joplin.create_note(title, content, note['parent_id'], **params)


def importer():
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


class JongToolKitImporter:
    """
        JongToolKitImporter:
        ====================

        Use it to import file in markdown from the cloud storage service

        example:

        >>> from jong_toolkit.jong_toolkit import JongToolKitImporter
        >>> file = '/somewhere/Dropbox/Applications/Joplin/letterbox/foorbar.md'
        >>> jtki = JongToolKitImporter()
        >>> jtki.import_note(file)
        >>> # or just withtout any parms to import all files
        >>> jtki.import_note()   # will grab the file in the path set in conf.py containing .jex or .md

    """

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

    def import_note(self, file):
        """
        importing a file
        :param file: file to import
        """
        self._joplin_run(file)


def collector():
    """
    read the folder of the file to import
    """
    jtkc = JongToolKitCollector()
    jtkc.update_notes()
