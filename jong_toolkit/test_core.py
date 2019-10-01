import configparser
import os
import unittest


class TestStringMethods(unittest.TestCase):

    def setUp(self):
        current_folder = os.path.dirname(__file__)
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(current_folder, 'settings.ini'))

    def test_config(self):
        self.assertTrue('JOPLIN_CONFIG' in self.config)
        self.assertTrue('JOPLIN_DEFAULT_TAG' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_NEW_TAG' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('PYPANDOC_MARKDOWN' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_IMPORT_FOLDER' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_PROFILE_PATH' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_DEFAULT_FOLDER' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_WEBCLIPPER' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_WEBCLIPPER_TOKEN' in self.config['JOPLIN_CONFIG'])
        self.assertTrue('JOPLIN_BIN_PATH' in self.config['JOPLIN_CONFIG'])

        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_TAG']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['PYPANDOC_MARKDOWN']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_IMPORT_FOLDER']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_PROFILE_PATH']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_DEFAULT_FOLDER']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_WEBCLIPPER_TOKEN']) is str)
        self.assertTrue(type(self.config['JOPLIN_CONFIG']['JOPLIN_BIN_PATH']) is str)


if __name__ == '__main__':
    unittest.main()
