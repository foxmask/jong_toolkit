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
import sys
import httpx

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
                    level=config['JOPLIN_CONFIG']['LOG_LEVEL'],
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = getLogger(__name__)


async def check_service():
    """
    check if the service is up before trying to use it
    :return:
    """
    url = '{}:{}/ping'.format(config['JOPLIN_CONFIG']['JOPLIN_URL'], config['JOPLIN_CONFIG']['JOPLIN_PORT'])
    try:
        res = httpx.get(url)
        if res.text == 'JoplinClipperServer':
            return True
        return False
    except httpx.HTTPError as e:
        print("Connection failed to {}. Check if joplin is started".format(url))
        print(e)
        print('Jong Toolkit aborted!')
        sys.exit(1)


def grab_note(note):
    """
    grab the webpage of that note
    :note :dict: dict of the shared note
    :return title of the grabed page and its body
    """
    # the body contains the URL all alone
    body = httpx.get(note['body'].strip())
    page = BeautifulSoup(body.text, 'html.parser')
    title = page.title.string if page.title else 'no title found'
    return title, page.body


async def collector():
    """
    create notes related to a given tag
    """
    if await check_service() is False:
        raise ConnectionError("Joplin service is not started")
    joplin_tag = config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_TAG']
    joplin_new_tag = config['JOPLIN_CONFIG']['JOPLIN_NEW_TAG']
    tags = await joplin.get_tags()
    for tag in tags.json():
        if tag['title'] == joplin_tag.lower():
            logger.debug(f'tag {tag}')
            tags_notes = await joplin.get_tags_notes(tag['id'])
            for note in tags_notes.json():
                logger.debug(f'note {note}')
                title, body = grab_note(note)
                params = {'source_url': note['body']}
                if joplin_new_tag:
                    params['tags'] = joplin_new_tag
                content = pypandoc.convert_text(body.decode(),
                                                config['JOPLIN_CONFIG']['PYPANDOC_MARKDOWN'],
                                                format='html')
                logger.info(f"new note {title}")
                res = await joplin.create_note(title, content, note['parent_id'], **params)
                if res.status_code == 200:
                    await joplin.delete_note(note['id'])


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
    print('Jong Toolkit started!')
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
    print('Jong Toolkit Finished!')
