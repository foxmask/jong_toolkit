# coding: utf-8
# python lib
import configparser
import itertools
import json
import os
from pathlib import Path
import shlex
import subprocess
from urllib.request import urlopen
# external lib
from joplin_api import JoplinApi
from bs4 import BeautifulSoup
import pypandoc
# JongToolKit
from command import JongToolKitCommand

cwd = Path.cwd()
config_file = str(cwd) + '/jong_toolkit/settings.ini'
config = configparser.ConfigParser()
config.read(config_file)
joplin = JoplinApi(token=config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN'])
pypandoc_markdown = config['JOPLIN_CONFIG']['PYPANDOC_MARKDOWN']

class JongToolKitCollector(JongToolKitCommand):
    """
    JongToolkit Collector class to deal with note to generate from a given tag
    """
    def get_tags_notes(self, tag):
        """
        get the note with the given tag
        """
        return joplin.get_tags_notes(tag)

    def grab_note(self, note):
        """
        grab the webpage of that note
        """
        body = urlopen(note['body'])
        page = BeautifulSoup(body, 'html.parser')
        return page.title.string, page.body

    def update_notes(self):
        joplin_tag = config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_TAG']
        tags = joplin.get_tags().json()
        for tag in tags:
            if tag['title'] == joplin_tag.lower():
                for note in self.get_tags_notes(tag['id']).json():
                    title, body = self.grab_note(note)
                    params = {'source_url': note['body']}
                    content = pypandoc.convert(body.decode(), pypandoc_markdown, format='html')                    
                    joplin.create_note(title, content, note['parent_id'], **params)


def go():
    """
    read the folder of the file to import
    """
    jtkc = JongToolKitCollector()
    jtkc.update_notes()

if __name__ == '__main__':
    go()
