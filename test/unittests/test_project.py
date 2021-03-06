"""Test project class"""

import os
import sys
import unittest

from clowder.model.project import Project
from clowder.model.source import Source
from unittests.shared import (
    __defaults_yaml__,
    __github_https_source_yaml__,
    __github_ssh_source_yaml__,
    __jules_group_yaml__,
    __jules_project_yaml__,
    __kishka_group_yaml__,
    __kishka_project_yaml__,
    __kit_group_yaml__,
    __kit_project_yaml__
)


class ProjectTest(unittest.TestCase):
    """project test subclass"""

    current_file_path = os.path.dirname(os.path.realpath(__file__))
    cats_example_path = os.path.abspath(os.path.join(current_file_path, '..', '..', 'examples', 'cats'))

    def setUp(self):

        # self.jules_project_path = os.path.join(self.CATS_EXAMPLE_PATH, 'black-cats', 'jules')
        # self.kishka_project_path = os.path.join(self.CATS_EXAMPLE_PATH, 'black-cats', 'kishka')
        self.kit_project_path = os.path.join(self.cats_example_path, 'black-cats', 'kit')
        sources = [Source(__github_ssh_source_yaml__), Source(__github_https_source_yaml__)]
        self.jules_project = Project(self.cats_example_path, __jules_project_yaml__,
                                     __jules_group_yaml__, __defaults_yaml__, sources)
        self.kishka_project = Project(self.cats_example_path, __kishka_project_yaml__,
                                      __kishka_group_yaml__, __defaults_yaml__, sources)
        self.kit_project = Project(self.cats_example_path, __kit_project_yaml__,
                                   __kit_group_yaml__, __defaults_yaml__, sources)

    def test_exists(self):
        """Test exists() method"""

        self.assertFalse(self.jules_project.exists())
        self.assertTrue(self.kit_project.exists())

    def test_full_path(self):
        """Test full_path() method"""

        self.assertEqual(self.kit_project.full_path(), self.kit_project_path)

    def test_is_dirty(self):
        """Test is_dirty() method"""

        self.assertTrue(self.kishka_project.is_dirty())
        self.assertFalse(self.kit_project.is_dirty())

    def test_is_valid(self):
        """Test is_valid() method"""

        self.assertTrue(self.jules_project.is_valid())
        self.assertFalse(self.kishka_project.is_valid())
        self.assertTrue(self.kit_project.is_valid())

    def test_member_variables(self):
        """Test the state of all project member variables initialized"""

        self.assertEqual(self.kit_project.name, 'jrgoodle/kit')
        self.assertEqual(self.kit_project.path, 'black-cats/kit')
        self.assertEqual(self.kit_project._ref, 'f2e20031ddce5cb097105f4d8ccbc77f4ac20709')
        self.assertEqual(self.kit_project._remote, 'origin')
        self.assertEqual(self.kit_project._root_directory, self.cats_example_path)
        self.assertEqual(self.kit_project._url, 'https://github.com/jrgoodle/kit.git')

    def test_get_yaml(self):
        """Test get_yaml() method"""

        project_yaml = {'name': 'jrgoodle/kit',
                        'path': 'black-cats/kit',
                        'depth': 0,
                        'recursive': False,
                        'ref': 'f2e20031ddce5cb097105f4d8ccbc77f4ac20709',
                        'remote': 'origin',
                        'source': 'github'}
        self.assertEqual(self.kit_project.get_yaml(), project_yaml)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        ProjectTest.cats_example_path = sys.argv.pop()
    unittest.main()
