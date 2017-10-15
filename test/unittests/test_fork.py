"""Test fork class"""

import os
import sys
import unittest
from test.unittests.shared import GITHUB_SSH_SOURCE_YAML
from clowder.fork import Fork
from clowder.source import Source


class ForkTest(unittest.TestCase):
    """fork test subclass"""

    CURRENT_FILE_DIR_PATH = os.path.dirname(os.path.realpath(__file__))
    CATS_EXAMPLE_PATH = os.path.abspath(os.path.join(CURRENT_FILE_DIR_PATH,
                                                     '..', '..', 'examples', 'cats'))

    def setUp(self):
        self.name = 'test_fork'
        self.remote_name = 'origin'
        self.fork_yaml = {'name': self.name, 'remote': self.remote_name}
        self.source = Source(GITHUB_SSH_SOURCE_YAML)
        self.root_directory = self.CATS_EXAMPLE_PATH
        self.path = 'fork/path'
        self.fork = Fork(self.fork_yaml, self.root_directory, self.path, self.source)

    def test_get_yaml(self):
        """Test get_yaml() method"""
        self.assertEqual(self.fork.get_yaml(), self.fork_yaml)

    def test_member_variables(self):
        """Test the state of all project member variables initialized"""
        self.assertEqual(self.fork.root_directory, self.root_directory)
        self.assertEqual(self.fork.path, self.path)
        self.assertEqual(self.fork.name, self.name)
        self.assertEqual(self.fork.remote_name, self.remote_name)
        self.assertEqual(self.fork.url, self.source.get_url_prefix() + self.name + ".git")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ForkTest.CATS_EXAMPLE_PATH = sys.argv.pop()
    unittest.main()