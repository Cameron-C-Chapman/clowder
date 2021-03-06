"""Test fork class"""

import os
import sys
import unittest

from clowder.model.fork import Fork
from clowder.model.source import Source
from unittests.shared import __github_ssh_source_yaml__


class ForkTest(unittest.TestCase):
    """fork test subclass"""

    current_file_path = os.path.dirname(os.path.realpath(__file__))
    cats_example_path = os.path.abspath(os.path.join(current_file_path, '..', '..', 'examples', 'cats'))

    def setUp(self):

        self.name = 'test_fork'
        self.remote_name = 'origin'
        self.fork_yaml = {'name': self.name, 'remote': self.remote_name}
        self.source = Source(__github_ssh_source_yaml__)
        self.root_directory = self.cats_example_path
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
        ForkTest.cats_example_path = sys.argv.pop()
    unittest.main()
