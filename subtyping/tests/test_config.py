""" This module tests the config_wrapper module. """

import unittest
import numbers
from subtyping.config_wrapper import Config


class TestConfigWrapper(unittest.TestCase):
    """ Test the ConfigWrapper class """

    def setUp(self):
        """ Prepare for tests, so load prepared config. """

        Config.parse_config_file('example_config.yaml')

    def test_config_dict_set(self):
        """ Config.config should not be the empty dict anymore """
        self.assertNotEqual(Config.config, {})

    def test_modules_replaced(self):
        """ Test if the string from 'module' attributes correctly
        have been replaced with python modules"""
        params = Config.config['Parameters']

        self.assertEqual(params['module'], numbers)
        self.assertEqual(params['list'][0]['module'], numbers)

    def test_classes_replaced(self):
        """ Test if the string from 'class' attributes correctly
        have been replaced with the corresponding python class """
        params = Config.config['Parameters']

        self.assertEqual(params['class'], numbers.Number)
        self.assertEqual(params['list'][1]['class'], numbers.Number)
