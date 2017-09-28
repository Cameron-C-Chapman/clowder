"""Representation of clowder.yaml project"""
import os
import sys
from termcolor import cprint
from clowder.fork import Fork
from clowder.utility.clowder_utilities import (
    execute_forall_command,
    is_internet_connection_available
)
from clowder.utility.print_utilities import (
    format_command,
    format_fork_string,
    print_command_failed_error
)
from clowder.utility.git_print_utilities import (
    format_project_string,
    format_project_ref_string,
    print_exists,
    print_validation
)
from clowder.utility.git_utilities import (
    git_configure_remotes,
    git_existing_local_branch,
    git_existing_remote_branch,
    git_existing_repository,
    git_fetch_remote,
    git_herd,
    git_herd_branch,
    git_herd_branch_upstream,
    git_herd_upstream,
    git_is_dirty,
    git_print_branches,
    git_prune_local,
    git_prune_remote,
    git_reset_head,
    git_sha_long,
    git_start,
    git_start_offline,
    git_stash,
    git_status,
    git_sync,
    git_validate_repo_state
)

# Disable errors shown by pylint for too many branches
# pylint: disable=R0912
# Disable errors shown by pylint for too many arguments
# pylint: disable=R0913
# Disable errors shown by pylint for too many instance attributes
# pylint: disable=R0902
# Disable errors shown by pylint for no specified exception types
# pylint: disable=W0702

class Project(object):
    """clowder.yaml project class"""

    def __init__(self, root_directory, project, group, defaults, sources):
        self.root_directory = root_directory
        self.name = project['name']
        self.path = project['path']

        if 'depth' in project:
            self.depth = project['depth']
        elif 'depth' in group:
            self.depth = group['depth']
        else:
            self.depth = defaults['depth']

        if 'ref' in project:
            self.ref = project['ref']
        elif 'ref' in group:
            self.ref = group['ref']
        else:
            self.ref = defaults['ref']

        if 'remote' in project:
            self.remote_name = project['remote']
        elif 'remote' in group:
            self.remote_name = group['remote']
        else:
            self.remote_name = defaults['remote']

        if 'source' in project:
            source_name = project['source']
        elif 'source' in group:
            source_name = group['source']
        else:
            source_name = defaults['source']

        for source in sources:
            if source.name == source_name:
                self.source = source

        self.url = self.source.get_url_prefix() + self.name + ".git"

        self.fork = None
        if 'fork' in project:
            fork = project['fork']
            self.fork = Fork(fork, self.root_directory, self.path, self.source)

    def branch(self, local=False, remote=False):
        """Print branches for project"""
        self._print_status()
        if not os.path.isdir(self.full_path()):
            cprint(" - Project is missing\n", 'red')
            return
        if is_internet_connection_available():
            if remote:
                if self.fork is None:
                    git_fetch_remote(self.full_path(), self.remote_name, self.depth)
                else:
                    git_fetch_remote(self.full_path(), self.fork.remote_name, 0)
                    git_fetch_remote(self.full_path(), self.remote_name, 0)
        git_print_branches(self.full_path(), local=local, remote=remote)

    def clean(self):
        """Discard changes for project"""
        if self.is_dirty():
            self._print_status()
            print(' - Discard current changes')
            git_reset_head(self.full_path())

    def diff(self):
        """Show git diff for project"""
        self._print_status()
        if not os.path.isdir(self.full_path()):
            cprint(" - Project is missing\n", 'red')
            return
        git_status(self.full_path())

    def exists(self):
        """Check if project exists on disk"""
        path = os.path.join(self.full_path())
        return os.path.isdir(path)

    def existing_branch(self, branch, is_remote):
        """Check if branch exists"""
        if is_remote:
            if self.fork is None:
                return git_existing_remote_branch(self.full_path(), branch, self.remote_name)
            else:
                return git_existing_remote_branch(self.full_path(), branch, self.fork.remote_name)
        else:
            return git_existing_local_branch(self.full_path(), branch)

    def fetch_all(self):
        """Fetch upstream changes if project exists on disk"""
        self._print_status()
        if self.exists():
            if self.fork is None:
                git_fetch_remote(self.full_path(), self.remote_name, self.depth)
            else:
                git_fetch_remote(self.full_path(), self.fork.remote_name, 0)
                git_fetch_remote(self.full_path(), self.remote_name, 0)
        else:
            self.print_exists()

    def formatted_project_path(self):
        """Return formatted project path"""
        repo_path = os.path.join(self.root_directory, self.path)
        return format_project_string(repo_path, self.path)

    def full_path(self):
        """Return full path to project"""
        return os.path.join(self.root_directory, self.path)

    def get_yaml(self):
        """Return python object representation for saving yaml"""
        project = {'name': self.name,
                   'path': self.path,
                   'depth': self.depth,
                   'ref': git_sha_long(self.full_path()),
                   'remote': self.remote_name,
                   'source': self.source.name}
        if self.fork is not None:
            fork_yaml = self.fork.get_yaml()
            project['fork'] = fork_yaml
        return project

    def herd(self, branch=None, depth=None):
        """Clone project or update latest from upstream"""
        if depth is None:
            herd_depth = self.depth
        else:
            herd_depth = depth

        if branch is None:
            if self.fork is None:
                self._print_status()
                git_herd(self.full_path(), self.url, self.remote_name, self.ref, herd_depth)
            else:
                self.fork.print_status()
                git_configure_remotes(self.full_path(), self.remote_name, self.url,
                                      self.fork.remote_name, self.fork.url)
                print(format_fork_string(self.fork.name))
                git_herd(self.full_path(), self.fork.url, self.fork.remote_name,
                         self.ref, 0)
                print(format_fork_string(self.name))
                git_herd_upstream(self.full_path(), self.url, self.remote_name,
                                  self.ref, 0)
        else:
            if self.fork is None:
                self._print_status()
                git_herd_branch(self.full_path(), self.url, self.remote_name,
                                branch, self.ref, herd_depth)
            else:
                self.fork.print_status()
                git_configure_remotes(self.full_path(), self.remote_name, self.url,
                                      self.fork.remote_name, self.fork.url)
                print(format_fork_string(self.fork.name))
                git_herd_branch(self.full_path(), self.fork.url, self.fork.remote_name,
                                branch, self.ref, 0)
                print(format_fork_string(self.name))
                git_herd_branch_upstream(self.full_path(), self.url, self.remote_name,
                                         branch, self.ref, 0)

    def is_dirty(self):
        """Check if project is dirty"""
        return git_is_dirty(self.full_path())

    def is_valid(self):
        """Validate status of project"""
        return git_validate_repo_state(self.full_path())

    def print_exists(self):
        """Print existence validation message for project"""
        if not self.exists():
            self._print_status()
            print_exists(self.full_path())

    def print_validation(self):
        """Print validation message for project"""
        if not self.is_valid():
            self._print_status()
            print_validation(self.full_path())

    def prune(self, branch, force=False, local=False, remote=False):
        """Prune branch"""
        if not git_existing_repository(self.full_path()):
            return
        if local and remote:
            self._prune_local(branch, force)
            self._prune_remote(branch)
        elif local:
            self._prune_local(branch, force)
        elif remote:
            self._prune_remote(branch)

    def run(self, command, ignore_errors):
        """Run command or script in project directory"""
        self._print_status()
        if not os.path.isdir(self.full_path()):
            cprint(" - Project is missing\n", 'red')
            return
        print(format_command(command))
        if self.fork is None:
            fork_remote = None
        else:
            fork_remote = self.fork.remote_name
        return_code = execute_forall_command(command.split(),
                                             self.full_path(),
                                             self.root_directory,
                                             self.name,
                                             self.remote_name,
                                             fork_remote,
                                             self.ref)
        if not ignore_errors:
            if return_code != 0:
                print_command_failed_error(command)
                sys.exit(return_code)

    def start(self, branch, tracking):
        """Start a new feature branch"""
        self._print_status()
        if not git_existing_repository(self.full_path()):
            cprint(" - Directory doesn't exist", 'red')
            return
        if self.fork is None:
            remote = self.remote_name
            depth = self.depth
        else:
            remote = self.fork.remote_name
            depth = 0
        if is_internet_connection_available():
            git_start(self.full_path(), remote, branch, depth, tracking)
        else:
            git_start_offline(self.full_path(), branch)

    def status(self, padding):
        """Print status for project"""
        self._print_status_indented(padding)

    def stash(self):
        """Stash changes for project if dirty"""
        if self.is_dirty():
            self._print_status()
            git_stash(self.full_path())

    def sync(self):
        """Print status for project"""
        self.fork.print_status()
        git_configure_remotes(self.full_path(), self.remote_name, self.url,
                              self.fork.remote_name, self.fork.url)
        print(format_fork_string(self.fork.name))
        git_herd(self.full_path(), self.fork.url, self.fork.remote_name,
                 self.ref, 0)
        print(format_fork_string(self.name))
        git_herd_upstream(self.full_path(), self.url, self.remote_name,
                          self.ref, 0)
        self.fork.print_status()
        git_sync(self.full_path(), self.remote_name, self.fork.remote_name, self.ref)

    def _print_status(self):
        """Print formatted project status"""
        repo_path = os.path.join(self.root_directory, self.path)
        if not git_existing_repository(repo_path):
            cprint(self.path, 'green')
            return
        project_output = format_project_string(repo_path, self.path)
        current_ref_output = format_project_ref_string(repo_path)
        print(project_output + ' ' + current_ref_output)

    def _print_status_indented(self, padding):
        """Print formatted and indented project status"""
        repo_path = os.path.join(self.root_directory, self.path)
        if not git_existing_repository(repo_path):
            cprint(self.name, 'green')
            return
        project_output = format_project_string(repo_path, self.path)
        current_ref_output = format_project_ref_string(repo_path)
        print('{0} {1}'.format(project_output.ljust(padding), current_ref_output))

    def _prune_local(self, branch, force):
        """Prune local branch"""
        if git_existing_local_branch(self.full_path(), branch):
            self._print_status()
            git_prune_local(self.full_path(), branch, self.ref, force)

    def _prune_remote(self, branch):
        """Prune remote branch"""
        if self.fork is None:
            remote = self.remote_name
        else:
            remote = self.fork.remote_name
        if git_existing_remote_branch(self.full_path(), branch, remote):
            self._print_status()
            git_prune_remote(self.full_path(), branch, remote)
