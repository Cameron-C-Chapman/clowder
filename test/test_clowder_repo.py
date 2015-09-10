"""Test ClowderRepo class"""
import os, unittest
from clowder.clowder_repo import ClowderRepo
from test.shared import CATS_EXAMPLE_PATH

class ClowderRepoTest(unittest.TestCase):
    """clowder_repo test subclass"""
    def setUp(self):
        self.clowder_repo = ClowderRepo(CATS_EXAMPLE_PATH)
        self.clowder_yaml_path = os.path.join(CATS_EXAMPLE_PATH, 'clowder.yaml')

    def test_member_variables(self):
        """Test the state of all project member variables initialized"""
        self.assertEqual(self.clowder_repo.root_directory, CATS_EXAMPLE_PATH)
        clowder_path = os.path.join(CATS_EXAMPLE_PATH, 'clowder')
        self.assertEqual(self.clowder_repo.clowder_path, clowder_path)

    def test_symlink_yaml(self):
        """Test symlink_yaml() method"""
        self.clowder_repo.symlink_yaml()
        self.assertEqual(os.readlink(self.clowder_yaml_path),
                         os.path.join(CATS_EXAMPLE_PATH, 'clowder', 'clowder.yaml'))

    def test_symlink_yaml_version(self):
        """Test symlink_yaml() method"""
        self.clowder_repo.symlink_yaml('v0.1')
        version_path = os.path.join('clowder', 'versions', 'v0.1', 'clowder.yaml')
        self.assertEqual(os.readlink(self.clowder_yaml_path),
                         os.path.join(CATS_EXAMPLE_PATH, version_path))

if __name__ == '__main__':
    unittest.main()
