"""Test source class"""

import sys
import unittest

from clowder import Source
from unittests.shared import (
    __github_https_source_yaml__,
    __github_ssh_source_yaml__
)


class SourceTest(unittest.TestCase):
    """source test subclass"""

    def setUp(self):

        self.ssh_source = Source(__github_ssh_source_yaml__)
        self.https_source = Source(__github_https_source_yaml__)

    def test_get_yaml(self):
        """Test get_yaml() method"""

        self.assertEqual(self.ssh_source.get_yaml(), __github_ssh_source_yaml__)
        self.assertEqual(self.https_source.get_yaml(), __github_https_source_yaml__)

    def test_https_url_prefix(self):
        """Test https url prefix"""

        self.assertEqual(self.https_source.get_url_prefix(), 'https://github.com/')

    def test_member_variables(self):
        """Test the state of all project member variables initialized"""

        self.assertEqual(self.ssh_source.name, 'github-ssh')
        self.assertEqual(self.ssh_source.url, 'ssh://git@github.com')
        self.assertEqual(self.https_source.name, 'github')
        self.assertEqual(self.https_source.url, 'https://github.com')

    def test_ssh_url_prefix(self):
        """Test ssh url prefix"""

        self.assertEqual(self.ssh_source.get_url_prefix(), 'git@github.com:')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        _ = sys.argv.pop()
    unittest.main()
