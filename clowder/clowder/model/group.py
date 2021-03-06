"""Representation of clowder.yaml group"""

from __future__ import print_function

import clowder.util.formatting as fmt
from clowder.model.project import Project


class Group(object):
    """clowder.yaml group class"""

    def __init__(self, root_directory, group, defaults, sources):

        self.name = group['name']
        self.depth = group.get('depth', defaults['depth'])
        self.recursive = group.get('recursive', defaults.get('recursive', False))
        self.timestamp_author = group.get('timestamp_author', defaults.get('timestamp_author', None))
        self.ref = group.get('ref', defaults['ref'])
        self.remote_name = group.get('remote', defaults['remote'])
        source_name = group.get('source', defaults['source'])

        for source in sources:
            if source.name == source_name:
                self.source = source

        self.projects = [Project(root_directory, p, group, defaults, sources) for p in group['projects']]
        self.projects.sort(key=lambda p: p.path)

    def existing_branch(self, branch, is_remote):
        """Checks whether at least one branch exists"""

        return any([p.existing_branch(branch, is_remote=is_remote) for p in self.projects])

    def existing_projects(self):
        """Validate existence status of all projects"""

        return all([project.exists() for project in self.projects])

    def get_yaml(self):
        """Return python object representation for saving yaml"""

        projects_yaml = [p.get_yaml() for p in self.projects]
        return {'name': self.name, 'projects': projects_yaml}

    def get_yaml_resolved(self):
        """Return python object representation for resolved yaml"""

        projects_yaml = [p.get_yaml(resolved=True) for p in self.projects]

        group = {'name': self.name,
                 'depth': self.depth,
                 'ref': self.ref,
                 'recursive': self.recursive,
                 'remote': self.remote_name,
                 'source': self.source.name,
                 'projects': projects_yaml}

        if self.timestamp_author:
            group['timestamp_author'] = self.timestamp_author

        return group

    def is_dirty(self):
        """Check if group has at least one dirty project"""

        return any([project.is_dirty() for project in self.projects])

    def is_valid(self):
        """Validate status of all projects"""

        return all([project.is_valid() for project in self.projects])

    def print_existence_message(self):
        """Print existence validation message for projects in group"""

        if self.existing_projects():
            return

        print(fmt.group_name(self.name))
        for project in self.projects:
            project.print_exists()

    def print_validation(self):
        """Print validation message for projects in group"""

        if self.is_valid():
            return

        print(fmt.group_name(self.name))
        for project in self.projects:
            project.print_validation()
