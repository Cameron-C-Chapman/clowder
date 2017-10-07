"""Git utilities"""
import os
import subprocess
import sys
from git import Repo
from termcolor import colored, cprint
from clowder.utility.clowder_utilities import (
    execute_command,
    existing_git_repository,
    ref_type,
    remove_directory_exit,
    truncate_ref
)
from clowder.utility.print_utilities import (
    format_command,
    format_path,
    format_ref_string,
    format_remote_string,
    print_command_failed_error,
    print_error,
    print_remote_already_exists_error
)

# Disable errors shown by pylint for no specified exception types
# pylint: disable=W0702
# Disable errors shown by pylint for catching too general exception Exception
# pylint: disable=W0703
# Disable errors shown by pylint for too many arguments
# pylint: disable=R0913

class Git(object):
    """Class encapsulating git utilities"""
    def __init__(self, repo_path):
        self.repo_path = repo_path
        if not existing_git_repository(self.repo_path):
            self.repo = None
            return
        self.repo = self._repo()

    def abort_rebase(self):
        """Abort rebase"""
        if not self.is_rebase_in_progress():
            return
        try:
            self.repo.git.rebase('--abort')
        except Exception as err:
            cprint(' - Failed to abort rebase', 'red')
            print_error(err)
            sys.exit(1)

    def add(self, files):
        """Add files to git index"""
        try:
            print(' - Add files to git index')
            print(self.repo.git.add(files))
        except Exception as err:
            cprint(' - Failed to add files to git index', 'red')
            print_error(err)
            sys.exit(1)

    def branches(self,):
        """Get list of current branches"""
        return self.repo.branches

    def checkout(self, truncated_ref):
        """Checkout git ref"""
        ref_output = format_ref_string(truncated_ref)
        try:
            print(' - Check out ' + ref_output)
            print(self.repo.git.checkout(truncated_ref))
        except Exception as err:
            message = colored(' - Failed to checkout ref ', 'red')
            print(message + ref_output)
            print_error(err)
            sys.exit(1)

    def clean(self, args=None):
        """Clean git directory"""
        clean_args = '-f'
        if args is not None:
            clean_args += args
        try:
            self.repo.git.clean(clean_args)
        except Exception as err:
            cprint(' - Failed to clean git repo', 'red')
            print_error(err)
            sys.exit(1)

    def commit(self, message):
        """Commit current changes"""
        print(' - Commit current changes')
        print(self.repo.git.commit(message=message))

    def configure_remotes(self, upstream_remote_name, upstream_remote_url,
                          fork_remote_name, fork_remote_url):
        """Configure remotes names for fork and upstream"""
        if not existing_git_repository(self.repo_path):
            return
        try:
            remotes = self.repo.remotes
        except:
            return
        else:
            for remote in remotes:
                if upstream_remote_url == self.repo.git.remote('get-url', remote.name):
                    if remote.name != upstream_remote_name:
                        self._rename_remote(remote.name, upstream_remote_name)
                        continue
                if fork_remote_url == self.repo.git.remote('get-url', remote.name):
                    if remote.name != fork_remote_name:
                        self._rename_remote(remote.name, fork_remote_name)
            remote_names = [r.name for r in self.repo.remotes]
            if upstream_remote_name in remote_names:
                if upstream_remote_url != self.repo.git.remote('get-url', upstream_remote_name):
                    actual_url = self.repo.git.remote('get-url', upstream_remote_name)
                    print_remote_already_exists_error(upstream_remote_name,
                                                      upstream_remote_url, actual_url)
                    sys.exit(1)
            if fork_remote_name in remote_names:
                if fork_remote_url != self.repo.git.remote('get-url', fork_remote_name):
                    actual_url = self.repo.git.remote('get-url', fork_remote_name)
                    print_remote_already_exists_error(fork_remote_name,
                                                      fork_remote_url, actual_url)
                    sys.exit(1)

    def create_repo(self, url, remote, ref, depth=0, recursive=False):
        """Clone git repo from url at path"""
        if existing_git_repository(self.repo_path):
            return
        if not os.path.isdir(self.repo_path):
            os.makedirs(self.repo_path)
        repo_path_output = format_path(self.repo_path)
        print(' - Clone repo at ' + repo_path_output)
        self._init_repo()
        remote_names = [r.name for r in self.repo.remotes]
        if remote in remote_names:
            self._checkout_ref(ref, remote, depth)
            return
        return_code = self._create_remote(remote, url)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        if ref_type(ref) is 'branch':
            self._checkout_new_repo_branch(truncate_ref(ref), remote, depth)
        elif ref_type(ref) is 'tag':
            self._checkout_new_repo_tag(truncate_ref(ref), remote, depth)
        elif ref_type(ref) is 'sha':
            self._checkout_new_repo_commit(ref, remote, depth)
        else:
            ref_output = format_ref_string(ref)
            print('Unknown ref ' + ref_output)
        if recursive:
            self.submodule_update_recursive(depth)

    def current_branch(self):
        """Return currently checked out branch of project"""
        return self.repo.head.ref.name

    def existing_remote_branch(self, branch, remote):
        """Check if remote branch exists"""
        try:
            origin = self.repo.remotes[remote]
        except:
            return False
        else:
            return branch in origin.refs

    def existing_local_branch(self, branch):
        """Check if local branch exists"""
        return branch in self.repo.heads

    def fetch(self, remote, ref=None, depth=0):
        """Fetch from a specific remote ref"""
        remote_output = format_remote_string(remote)
        if depth == 0:
            print(' - Fetch from ' + remote_output)
            message = colored(' - Failed to fetch from ', 'red')
            error = message + remote_output
            command = ['git', 'fetch', remote, '--prune', '--tags']
        else:
            if ref is None:
                command = ['git', 'fetch', remote, '--depth', str(depth), '--prune', '--tags']
                message = colored(' - Failed to fetch remote ', 'red')
                error = message + remote_output
            else:
                ref_output = format_ref_string(truncate_ref(ref))
                print(' - Fetch from ' + remote_output + ' ' + ref_output)
                message = colored(' - Failed to fetch from ', 'red')
                error = message + remote_output + ' ' + ref_output
                command = ['git', 'fetch', remote, truncate_ref(ref),
                           '--depth', str(depth), '--prune']
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            print(error)
            print_command_failed_error(command)
        return return_code

    def fetch_silent(self):
        """Perform a git fetch"""
        command = ['git', 'fetch', '--all', '--prune', '--tags']
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            cprint(' - Failed to fetch', 'red')
            print_command_failed_error(command)
            sys.exit(return_code)

    def has_submodules(self):
        """Repo has submodules"""
        if self.repo.submodules.count > 0:
            return True
        return False

    def herd(self, url, remote, ref, depth=0, recursive=False, fetch=True):
        """Herd ref"""
        if not existing_git_repository(self.repo_path):
            self.create_repo(url, remote, ref, depth=depth, recursive=recursive)
            return
        if ref_type(ref) is 'branch':
            return_code = self._create_remote(remote, url)
            if return_code != 0:
                sys.exit(1)
            self._checkout_ref(ref, remote, depth, fetch=fetch)
            branch = truncate_ref(ref)
            if self.existing_remote_branch(branch, remote):
                if self._is_tracking_branch(branch):
                    self._pull_remote_branch(remote, branch)
                else:
                    self._set_tracking_branch_same_commit(branch, remote, depth)
        elif ref_type(ref) is 'tag' or ref_type(ref) is 'sha':
            return_code = self._create_remote(remote, url)
            if return_code != 0:
                sys.exit(1)
            self._checkout_ref(ref, remote, depth)
        else:
            cprint('Unknown ref ' + ref, 'red')
            sys.exit(1)
        if recursive:
            self.submodule_update_recursive(depth)

    def herd_branch(self, url, remote, branch, default_ref, depth=0, recursive=False):
        """Herd branch"""
        if not existing_git_repository(self.repo_path):
            self._create_repo_herd_branch(url, remote, branch,
                                          default_ref, depth=depth, recursive=recursive)
            return
        return_code = self.fetch(remote, depth=depth, ref=branch)
        if return_code != 0:
            self.herd(url, remote, default_ref, depth=depth, recursive=recursive)
            return
        if self.existing_local_branch(branch):
            self._checkout_ref('refs/heads/' + branch, remote, depth)
            if self.existing_remote_branch(branch, remote):
                if self._is_tracking_branch(branch):
                    self._pull_remote_branch(remote, branch)
                else:
                    self._set_tracking_branch_same_commit(branch, remote, depth)
        elif self.existing_remote_branch(branch, remote):
            self.herd(url, remote, 'refs/heads/' + branch, depth=depth,
                          recursive=recursive, fetch=False)
        else:
            self.herd(url, remote, default_ref, depth=depth, recursive=recursive)
        if recursive:
            self.submodule_update_recursive(depth)

    def herd_branch_upstream(self, url, remote, branch, default_ref, depth=0):
        """Herd branch for fork's upstream repo"""
        return_code = self._create_remote(remote, url)
        if return_code != 0:
            sys.exit(1)
        return_code = self.fetch(remote, depth=depth, ref=branch)
        if depth != 0 and return_code != 0:
            self.fetch(remote, depth=depth, ref=default_ref)

    def herd_upstream(self, url, remote, ref, depth=0):
        """Herd branch for fork's upstream repo"""
        return_code = self._create_remote(remote, url)
        if return_code != 0:
            sys.exit(1)
        self.fetch(remote, depth=depth, ref=ref)

    def is_detached(self):
        """Check if HEAD is detached"""
        if not os.path.isdir(self.repo_path):
            return False
        else:
            return self.repo.head.is_detached

    def is_dirty(self, path):
        """Check if repo is dirty"""
        if not os.path.isdir(path):
            return False
        else:
            try:
                return self.repo.is_dirty()
            except Exception as err:
                repo_path_output = format_path(path)
                message = colored("Failed to create Repo instance for ", 'red')
                print(message + repo_path_output)
                print_error(err)
                sys.exit(1)

    def is_rebase_in_progress(self):
        """Detect whether rebase is in progress"""
        rebase_apply = os.path.join(self.repo_path, '.git', 'rebase-apply')
        rebase_merge = os.path.join(self.repo_path, '.git', 'rebase-merge')
        is_rebase_apply = os.path.isdir(rebase_apply)
        is_rebase_merge = os.path.isdir(rebase_merge)
        return is_rebase_apply or is_rebase_merge

    def is_valid_repo(self):
        """Validate repo"""
        if self.is_dirty(self.repo_path):
            return False
        elif self.is_rebase_in_progress():
            return False
        elif self.untracked_files():
            return False
        else:
            return True

    def is_valid_submodule(self, path):
        """Validate repo"""
        if self.is_dirty(path):
            return False
        # elif untracked_files(repo_path):
        #     return False
        else:
            return True

    def new_commits(self, upstream=False):
        """Returns the number of new commits"""
        try:
            local_branch = self.repo.active_branch
        except:
            return 0
        else:
            if local_branch is None:
                return 0
            tracking_branch = local_branch.tracking_branch()
            if tracking_branch is None:
                return 0
            try:
                commits = local_branch.commit.hexsha + '...' + tracking_branch.commit.hexsha
                rev_list_count = self.repo.git.rev_list('--count', '--left-right', commits)
                if upstream:
                    count = str(rev_list_count).split()[1]
                else:
                    count = str(rev_list_count).split()[0]
                return count
            except:
                return 0

    def print_branches(self, local=False, remote=False):
        """Print branches"""
        if local and remote:
            command = ['git', 'branch', '-a']
        elif local:
            command = ['git', 'branch']
        elif remote:
            command = ['git', 'branch', '-r']
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            cprint(' - Failed to print branches', 'red')
            print_command_failed_error(command)
            sys.exit(return_code)

    def prune_local(self, branch, default_ref, force):
        """Prune branch in repository"""
        branch_output = format_ref_string(branch)
        if branch not in self.repo.heads:
            print(' - Local branch ' + branch_output + " doesn't exist")
            return
        prune_branch = self.repo.heads[branch]
        if self.repo.head.ref == prune_branch:
            ref_output = format_ref_string(truncate_ref(default_ref))
            try:
                print(' - Checkout ref ' + ref_output)
                self.repo.git.checkout(truncate_ref(default_ref))
            except Exception as err:
                message = colored(' - Failed to checkout ref', 'red')
                print(message + ref_output)
                print_error(err)
                sys.exit(1)
        try:
            print(' - Delete local branch ' + branch_output)
            self.repo.delete_head(branch, force=force)
            return
        except Exception as err:
            message = colored(' - Failed to delete local branch ', 'red')
            print(message + branch_output)
            print_error(err)
            sys.exit(1)

    def prune_remote(self, branch, remote):
        """Prune remote branch in repository"""
        origin = self._remote(remote)
        if origin is None:
            sys.exit(1)
        branch_output = format_ref_string(branch)
        if branch not in origin.refs:
            print(' - Remote branch ' + branch_output + " doesn't exist")
            return
        try:
            print(' - Delete remote branch ' + branch_output)
            self.repo.git.push(remote, '--delete', branch)
        except Exception as err:
            message = colored(' - Failed to delete remote branch ', 'red')
            print(message + branch_output)
            print_error(err)
            sys.exit(1)

    def pull(self):
        """Pull from remote branch"""
        if self.repo.head.is_detached:
            print(' - HEAD is detached')
            return
        try:
            print(' - Pull latest changes')
            print(self.repo.git.pull())
        except Exception as err:
            cprint(' - Failed to pull latest changes', 'red')
            print_error(err)
            sys.exit(1)

    def push(self):
        """Push to remote branch"""
        if self.repo.head.is_detached:
            print(' - HEAD is detached')
            return
        try:
            print(' - Push local changes')
            print(self.repo.git.push())
        except Exception as err:
            cprint(' - Failed to push local changes', 'red')
            print_error(err)
            sys.exit(1)

    def reset_head(self):
        """Reset head of repo, discarding changes"""
        self.repo.head.reset(index=True, working_tree=True)

    def sha_long(self):
        """Return long sha for currently checked out commit"""
        return self.repo.head.commit.hexsha

    def sha_short(self):
        """Return short sha of currently checked out commit"""
        sha = self.repo.head.commit.hexsha
        return self.repo.git.rev_parse(sha, short=True)

    def start(self, remote, branch, depth, tracking):
        """Start new branch in repository"""
        if branch not in self.repo.heads:
            return_code = self.fetch(remote, depth=depth, ref=branch)
            if return_code != 0:
                sys.exit(return_code)
            return_code = self._create_branch_local(branch)
            if return_code != 0:
                sys.exit(return_code)
            return_code = self._checkout_branch_local(branch)
            if return_code != 0:
                sys.exit(return_code)
            if tracking:
                self._create_branch_remote_tracking(branch, remote, depth)
            return
        branch_output = format_ref_string(branch)
        print(' - ' + branch_output + ' already exists')
        correct_branch = self._is_branch_checked_out(branch)
        if correct_branch:
            print(' - On correct branch')
        else:
            return_code = self._checkout_branch_local(branch)
            if return_code != 0:
                sys.exit(return_code)
        if tracking:
            self._create_branch_remote_tracking(branch, remote, depth)

    def start_offline(self, branch):
        """Start new branch in repository when offline"""
        branch_output = format_ref_string(branch)
        if branch not in self.repo.heads:
            return_code = self._create_branch_local(branch)
            if return_code != 0:
                sys.exit(return_code)
            return_code = self._checkout_branch_local(branch)
            if return_code != 0:
                sys.exit(return_code)
            return
        print(' - ' + branch_output + ' already exists')
        correct_branch = self._is_branch_checked_out(branch)
        if correct_branch:
            print(' - On correct branch')
            return
        return_code = self._checkout_branch_local(branch)
        if return_code != 0:
            sys.exit(return_code)

    def stash(self):
        """Stash current changes in repository"""
        if self.repo.is_dirty():
            print(' - Stash current changes')
            self.repo.git.stash()
        else:
            print(' - No changes to stash')

    def status(self):
        """Print git status"""
        command = ['git', 'status', '-vv']
        print(format_command(command))
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            cprint(' - Failed to print status', 'red')
            print_command_failed_error(command)
            sys.exit(return_code)

    def submodules_clean(self):
        """Clean all submodules"""
        try:
            self.repo.git.submodule('foreach', '--recursive', 'git', 'clean', '-ffdx')
        except Exception as err:
            cprint(' - Failed to clean submodules', 'red')
            print_error(err)
            sys.exit(1)

    def submodules_reset(self):
        """Reset all submodules"""
        try:
            self.repo.git.submodule('foreach', '--recursive', 'git', 'reset', '--hard')
        except Exception as err:
            cprint(' - Failed to reset submodules', 'red')
            print_error(err)
            sys.exit(1)

    def submodules_update(self):
        """Update all submodules"""
        try:
            self.repo.git.submodule('update', '--checkout', '--recursive', '--force')
        except Exception as err:
            cprint(' - Failed to update submodules', 'red')
            print_error(err)
            sys.exit(1)

    def submodule_update_recursive(self, depth):
        """Update submodules recursively and initialize if not present"""
        print(' - Update submodules recursively and initialize if not present')
        if depth == 0:
            command = ['git', 'submodule', 'update', '--init', '--recursive']
        else:
            command = ['git', 'submodule', 'update', '--init', '--recursive', '--depth', depth]
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            cprint(' - Failed to update submodules', 'red')
            print_command_failed_error(command)
            sys.exit(return_code)

    def sync(self, upstream_remote, fork_remote, ref, recursive):
        """Sync fork with upstream remote"""
        print(' - Sync fork with upstream remote')
        if ref_type(ref) is not 'branch':
            cprint(' - Can only sync branches', 'red')
            sys.exit(1)
        fork_remote_output = format_remote_string(fork_remote)
        branch_output = format_ref_string(truncate_ref(ref))
        self._pull_remote_branch(upstream_remote, truncate_ref(ref))
        print(' - Push to ' + fork_remote_output + ' ' + branch_output)
        command = ['git', 'push', fork_remote, truncate_ref(ref)]
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            message = colored(' - Failed to push to ', 'red')
            print(message + fork_remote_output + ' ' + branch_output)
            print_command_failed_error(command)
            sys.exit(return_code)
        if recursive:
            self.submodule_update_recursive(recursive)

    def untracked_files(self):
        """Execute command and display continuous output"""
        command = "git ls-files -o -d --exclude-standard | sed q | wc -l| tr -d '[:space:]'"
        try:
            output = subprocess.check_output(command,
                                             shell=True,
                                             cwd=self.repo_path)
            return output.decode('utf-8') is '1'
        except Exception as err:
            cprint(' - Failed to check untracked files', 'red')
            print_error(err)
            sys.exit(1)

    def validate_repo(self):
        """Validate repo state"""
        if not existing_git_repository(self.repo_path):
            return True
        if not self.is_valid_repo():
            return False
        for submodule in self.repo.submodules:
            if not self.is_valid_submodule(submodule.path):
                return False
        return True

    def _checkout_branch_local(self, branch):
        """Checkout local branch"""
        branch_output = format_ref_string(branch)
        try:
            print(' - Checkout branch ' + branch_output)
            default_branch = self.repo.heads[branch]
            default_branch.checkout()
            return 0
        except Exception as err:
            message = colored(' - Failed to checkout branch ', 'red')
            print(message + branch_output)
            print_error(err)
            return 1

    def _checkout_new_repo_branch(self, branch, remote, depth):
        """Checkout remote branch or fail and delete repo if it doesn't exist"""
        branch_output = format_ref_string(branch)
        origin = self._remote(remote)
        if origin is None:
            remove_directory_exit(self.repo_path)
        return_code = self.fetch(remote, depth=depth, ref=branch)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        if not self.existing_remote_branch(branch, remote):
            message = colored(' - No existing remote branch ', 'red')
            print(message + branch_output)
            remove_directory_exit(self.repo_path)
        return_code = self._create_branch_local_tracking(branch, remote,
                                                         depth=depth, fetch=False)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        else:
            return_code = self._set_tracking_branch(remote, branch)
            if return_code != 0:
                remove_directory_exit(self.repo_path)
                return
            return_code = self._checkout_branch_local(branch)
            if return_code != 0:
                remove_directory_exit(self.repo_path)

    def _checkout_new_repo_commit(self, commit, remote, depth):
        """Checkout commit or fail and delete repo if it doesn't exist"""
        commit_output = format_ref_string(commit)
        origin = self._remote(remote)
        if origin is None:
            remove_directory_exit(self.repo_path)
        return_code = self.fetch(remote, depth=depth, ref=commit)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        print(' - Checkout commit ' + commit_output)
        try:
            self.repo.git.checkout(commit)
        except Exception as err:
            message = colored(' - Failed to checkout commit ', 'red')
            print(message + commit_output)
            print_error(err)
            remove_directory_exit(self.repo_path)

    def _checkout_new_repo_tag(self, tag, remote, depth):
        """Checkout tag or fail and delete repo if it doesn't exist"""
        tag_output = format_ref_string(tag)
        origin = self._remote(remote)
        if origin is None:
            remove_directory_exit(self.repo_path)
        return_code = self.fetch(remote, depth=depth, ref=tag)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        try:
            remote_tag = origin.tags[tag]
        except:
            message = colored(' - No existing remote tag ', 'red')
            print(message + tag_output)
            remove_directory_exit(self.repo_path)
        else:
            print(' - Checkout tag ' + tag_output)
            try:
                self.repo.git.checkout(remote_tag)
            except Exception as err:
                message = colored(' - Failed to checkout tag ', 'red')
                print(message + tag_output)
                print_error(err)
                remove_directory_exit(self.repo_path)

    def _checkout_ref(self, ref, remote, depth, fetch=True):
        """Checkout branch, tag, or commit from sha"""
        if ref_type(ref) is 'branch':
            branch = truncate_ref(ref)
            if not self.existing_local_branch(branch):
                return_code = self._create_branch_local_tracking(branch, remote,
                                                                 depth=depth, fetch=fetch)
                if return_code != 0:
                    sys.exit(return_code)
            if self._is_branch_checked_out(branch):
                branch_output = format_ref_string(branch)
                message_1 = ' - Branch '
                message_2 = ' already checked out'
                print(message_1 + branch_output + message_2)
                return
            self._checkout_branch_local(branch)
        elif ref_type(ref) is 'tag':
            self.fetch(remote, depth=depth, ref=ref)
            self._checkout_tag(truncate_ref(ref))
        elif ref_type(ref) is 'sha':
            self.fetch(remote, depth=depth, ref=ref)
            self._checkout_sha(ref)
        else:
            ref_output = format_ref_string(ref)
            print('Unknown ref ' + ref_output)

    def _checkout_sha(self, sha):
        """Checkout commit by sha"""
        correct_commit = False
        try:
            same_sha = self.repo.head.commit.hexsha == sha
            is_detached = self.repo.head.is_detached
        except:
            pass
        else:
            if same_sha and is_detached:
                print(' - On correct commit')
                correct_commit = True
        finally:
            if not correct_commit:
                commit_output = format_ref_string(sha)
                try:
                    print(' - Checkout commit ' + commit_output)
                    self.repo.git.checkout(sha)
                except Exception as err:
                    message = colored(' - Failed to checkout commit ', 'red')
                    print(message + commit_output)
                    print_error(err)
                    sys.exit(1)

    def _checkout_tag(self, tag):
        """Checkout commit tag is pointing to"""
        tag_output = format_ref_string(tag)
        correct_commit = False
        if tag not in self.repo.tags:
            print(' - No existing tag ' + tag_output)
            return
        try:
            same_commit = self.repo.head.commit == self.repo.tags[tag].commit
            is_detached = self.repo.head.is_detached
        except:
            pass
        else:
            if same_commit and is_detached:
                print(' - On correct commit for tag')
                correct_commit = True
        finally:
            if not correct_commit:
                try:
                    print(' - Checkout tag ' + tag_output)
                    self.repo.git.checkout(tag)
                except Exception as err:
                    message = colored(' - Failed to checkout tag ', 'red')
                    print(message + tag_output)
                    print_error(err)
                    sys.exit(1)


    def _create_branch_local(self, branch):
        """Create local branch"""
        branch_output = format_ref_string(branch)
        try:
            print(' - Create branch ' + branch_output)
            self.repo.create_head(branch)
            return 0
        except Exception as err:
            message = colored(' - Failed to create branch ', 'red')
            print(message + branch_output)
            print_error(err)
            return 1

    def _create_branch_local_tracking(self, branch, remote, depth, fetch=True):
        """Create and checkout tracking branch"""
        branch_output = format_ref_string(branch)
        origin = self._remote(remote)
        if origin is None:
            return 1
        if fetch:
            return_code = self.fetch(remote, depth=depth, ref=branch)
            if return_code != 0:
                return return_code
        try:
            print(' - Create branch ' + branch_output)
            self.repo.create_head(branch, origin.refs[branch])
        except Exception as err:
            message = colored(' - Failed to create branch ', 'red')
            print(message + branch_output)
            print_error(err)
            return 1
        else:
            return_code = self._set_tracking_branch(remote, branch)
            if return_code != 0:
                return return_code
            return self._checkout_branch_local(branch)

    def _create_branch_remote_tracking(self, branch, remote, depth):
        """Create remote tracking branch"""
        branch_output = format_ref_string(branch)
        origin = self._remote(remote)
        if origin is None:
            sys.exit(1)
        return_code = self.fetch(remote, depth=depth, ref=branch)
        if return_code != 0:
            sys.exit(return_code)
        if branch in origin.refs:
            try:
                self.repo.git.config('--get', 'branch.' + branch + '.merge')
            except:
                message_1 = colored(' - Remote branch ', 'red')
                message_2 = colored(' already exists', 'red')
                print(message_1 + branch_output + message_2 + '\n')
                sys.exit(1)
            else:
                print(' - Tracking branch ' + branch_output + ' already exists')
                return
        try:
            print(' - Push remote branch ' + branch_output)
            self.repo.git.push(remote, branch)
        except Exception as err:
            message = colored(' - Failed to push remote branch ', 'red')
            print(message + branch_output)
            print_error(err)
            sys.exit(1)
        else:
            return_code = self._set_tracking_branch(remote, branch)
            if return_code != 0:
                sys.exit(return_code)

    def _create_remote(self, remote, url):
        """Create new remote"""
        remote_names = [r.name for r in self.repo.remotes]
        if remote in remote_names:
            return 0
        remote_output = format_remote_string(remote)
        try:
            print(" - Create remote " + remote_output)
            self.repo.create_remote(remote, url)
            return 0
        except Exception as err:
            message = colored(" - Failed to create remote ", 'red')
            print(message + remote_output)
            print_error(err)
            return 1

    def _create_repo_herd_branch(self, url, remote, branch, default_ref,
                                 depth=0, recursive=False):
        """Clone git repo from url at path for herd branch"""
        if existing_git_repository(self.repo_path):
            return
        if not os.path.isdir(self.repo_path):
            os.makedirs(self.repo_path)
        repo_path_output = format_path(self.repo_path)
        print(' - Clone repo at ' + repo_path_output)
        self._init_repo()
        remote_names = [r.name for r in self.repo.remotes]
        if remote in remote_names:
            self._checkout_ref('refs/heads/' + branch, remote, depth)
            return
        return_code = self._create_remote(remote, url)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        branch_output = format_ref_string(branch)
        origin = self._remote(remote)
        if origin is None:
            remove_directory_exit(self.repo_path)
        return_code = self.fetch(remote, depth=depth, ref=branch)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        if not self.existing_remote_branch(branch, remote):
            print(' - No existing remote branch ' + branch_output)
            self._checkout_new_repo_branch(truncate_ref(default_ref), remote, depth)
            return
        return_code = self._create_branch_local_tracking(branch, remote,
                                                         depth=depth, fetch=False)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        return_code = self._set_tracking_branch(remote, branch)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        return_code = self._checkout_branch_local(branch)
        if return_code != 0:
            remove_directory_exit(self.repo_path)
        if recursive:
            self.submodule_update_recursive(depth)

    def _init_repo(self):
        """Clone repository"""
        try:
            self.repo = Repo.init(self.repo_path)
        except Exception as err:
            cprint(' - Failed to initialize repository', 'red')
            print_error(err)
            remove_directory_exit(self.repo_path)

    def _is_branch_checked_out(self, branch):
        """Check if branch is checked out"""
        try:
            default_branch = self.repo.heads[branch]
            not_detached = not self.repo.head.is_detached
            same_branch = self.repo.head.ref == default_branch
        except:
            return False
        else:
            return not_detached and same_branch

    def _is_tracking_branch(self, branch):
        """Check if branch is a tracking branch"""
        branch_output = format_ref_string(branch)
        try:
            local_branch = self.repo.heads[branch]
        except Exception as err:
            message = colored(' - No existing branch ', 'red')
            print(message + branch_output)
            print_error(err)
            sys.exit(1)
        else:
            tracking_branch = local_branch.tracking_branch()
            return True if tracking_branch else False

    def _pull_remote_branch(self, remote, branch):
        """Pull from remote branch"""
        if self.repo.head.is_detached:
            print(' - HEAD is detached')
            return
        branch_output = format_ref_string(branch)
        remote_output = format_remote_string(remote)
        print(' - Pull from ' + remote_output + ' ' + branch_output)
        command = ['git', 'pull', remote, branch]
        return_code = execute_command(command, self.repo_path)
        if return_code != 0:
            message = colored(' - Failed to pull from ', 'red')
            print(message + remote_output + ' ' + branch_output)
            print_command_failed_error(command)
            sys.exit(return_code)

    def _remote(self, remote):
        """Get remote"""
        remote_output = format_remote_string(remote)
        try:
            return self.repo.remotes[remote]
        except Exception as err:
            message = colored(' - No existing remote ', 'red')
            print(message + remote_output)
            print_error(err)
            return None

    def _rename_remote(self, remote_from, remote_to):
        """Rename remote"""
        remote_output_from = format_remote_string(remote_from)
        remote_output_to = format_remote_string(remote_to)
        print(' - Rename remote ' + remote_output_from + ' to ' + remote_output_to)
        try:
            self.repo.git.remote('rename', remote_from, remote_to)
        except Exception as err:
            cprint(' - Failed to rename remote', 'red')
            print_error(err)
            sys.exit(1)

    def _repo(self):
        """Create Repo instance for path"""
        try:
            repo = Repo(self.repo_path)
            return repo
        except Exception as err:
            repo_path_output = format_path(self.repo_path)
            message = colored("Failed to create Repo instance for ", 'red')
            print(message + repo_path_output)
            print_error(err)
            sys.exit(1)

    def _set_tracking_branch(self, remote, branch):
        """Set tracking branch"""
        branch_output = format_ref_string(branch)
        remote_output = format_remote_string(remote)
        origin = self._remote(remote)
        try:
            local_branch = self.repo.heads[branch]
            remote_branch = origin.refs[branch]
            print(' - Set tracking branch ' + branch_output +
                  ' -> ' + remote_output + ' ' + branch_output)
            local_branch.set_tracking_branch(remote_branch)
            return 0
        except Exception as err:
            message = colored(' - Failed to set tracking branch ', 'red')
            print(message + branch_output)
            print_error(err)
            return 1

    def _set_tracking_branch_same_commit(self, branch, remote, depth):
        """Set tracking relationship between local and remote branch if on same commit"""
        branch_output = format_ref_string(branch)
        origin = self._remote(remote)
        if origin is None:
            sys.exit(1)
        return_code = self.fetch(remote, depth=depth, ref=branch)
        if return_code != 0:
            sys.exit(return_code)
        if not self.existing_local_branch(branch):
            message_1 = colored(' - No local branch ', 'red')
            print(message_1 + branch_output + '\n')
            sys.exit(1)
        if not self.existing_remote_branch(branch, remote):
            message_1 = colored(' - No remote branch ', 'red')
            print(message_1 + branch_output + '\n')
            sys.exit(1)
        local_branch = self.repo.heads[branch]
        remote_branch = origin.refs[branch]
        if local_branch.commit != remote_branch.commit:
            message_1 = colored(' - Existing remote branch ', 'red')
            message_2 = colored(' on different commit', 'red')
            print(message_1 + branch_output + message_2 + '\n')
            sys.exit(1)
        return_code = self._set_tracking_branch(remote, branch)
        if return_code != 0:
            sys.exit(return_code)
