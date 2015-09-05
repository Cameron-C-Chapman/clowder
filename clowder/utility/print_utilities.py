"""Print utilities"""
import emoji, os, sys
from termcolor import colored, cprint
from clowder.utility.git_utilities import (
    git_current_sha,
    git_current_branch,
    git_is_detached,
    git_is_dirty
)

def format_project_string(repo_path, name):
    """Return formatted project name"""
    if git_is_dirty(repo_path):
        color = 'red'
        symbol = '*'
    else:
        color = 'green'
        symbol = ''
    return colored(name + symbol, color)

def format_ref_string(repo_path):
    """Return formatted repo ref name"""
    if git_is_detached(repo_path):
        current_ref = git_current_sha(repo_path)
        return colored('(HEAD @ ' + current_ref + ')', 'magenta')
    else:
        current_branch = git_current_branch(repo_path)
        return colored('(' + current_branch + ')', 'magenta')

def get_cat_face():
    """Return a cat emoji"""
    return emoji.emojize(':cat:', use_aliases=True)

def get_cat():
    """Return a cat emoji"""
    return emoji.emojize(':cat2:', use_aliases=True)

def print_clowder_repo_status(root_directory):
    """Print clowder repo status"""
    repo_path = os.path.join(root_directory, 'clowder')
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        output = colored('clowder', 'green')
        print(get_cat_face() + ' ' + output)
        return
    project_output = format_project_string(repo_path, 'clowder')
    current_ref_output = format_ref_string(repo_path)
    print(get_cat_face() + ' ' + project_output + ' ' + current_ref_output)

def print_exiting():
    """Print Exiting and exit with error code"""
    print('')
    cprint('Exiting...', 'red')
    print('')
    sys.exit(1)

def print_group(name):
    """Print formatted group name"""
    name_output = colored(name, attrs=['bold', 'underline'])
    print(name_output)

def print_validation(repo_path):
    """Print validation messages"""
    if not os.path.isdir(os.path.join(repo_path, '.git')):
        return
    if git_is_dirty(repo_path):
        print(' - Dirty repo. Please stash, commit, or discard your changes')
