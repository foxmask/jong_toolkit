# coding: utf-8
# python lib
import argparse
import asyncio
import configparser
import itertools
import logging
from logging import getLogger
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
if not config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN']:
    raise ValueError('Token not provided, edit the settings.ini and set JOPLIN_WEBCLIPPER_TOKEN accordingly')

joplin = JoplinApi(token=config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN'])

logging.basicConfig(filename='jong_toolkit.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger("joplin_api.api")


def grab_note(note):
    """
    grab the webpage of that note
    :note :dict: dict of the shared note
    :return title of the grabed page and its body
    """
    # the body contains the URL all alone
    body = urlopen(note['title'])
    page = BeautifulSoup(body, 'html.parser')
    title = page.title.string if page.title else 'no title found'
    return title, page.body


async def collector():
    """
    create notes related to a given tag
    """
    joplin_tag = config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_TAG']
    tags = await joplin.get_tags()
    for tag in tags.json():
        logger.info(f'tag {tag}')
        print(f"tag {tag}")
        if tag['title'] == joplin_tag.lower():
            tags_notes = await joplin.get_tags_notes(tag['id'])
            for note in tags_notes.json():
                logger.info(f'note {note}')
                print(note)
                title, body = grab_note(note)
                params = {'source_url': note['body']}
                content = pypandoc.convert_text(body.decode(), config['JOPLIN_CONFIG']['PYPANDOC_MARKDOWN'],
                                                format='html')
                await joplin.create_note(title, content, note['parent_id'], **params)


class JongToolKitImporter:
    """
        JongToolKitImporter:
        ====================

        Use it to import file in markdown from the cloud storage service

        example:

        >>> from jong_toolkit import JongToolKitImporter
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


if __name__ == '__main__':

    parser = argparse.ArgumentParser(prog="jong_toolkit/core.py", description='jong toolkit')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--collector', action='store_true')
    group.add_argument('--importer', action='store_true')
    args = parser.parse_args()
    if args.collector:
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(collector())
        finally:
            loop.close()
    else:
        importer()
