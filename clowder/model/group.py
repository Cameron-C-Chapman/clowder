"""Model representation of clowder.yaml group"""

from clowder.model.project import Project
from clowder.utility.print_utilities import print_group

class Group(object):
    """Model class for clowder.yaml group"""

    def __init__(self, rootDirectory, group, defaults, remotes):
        self.name = group['name']
        self.projects = []
        for project in group['projects']:
            self.projects.append(Project(rootDirectory, project, defaults, remotes))
        self.projects.sort(key=lambda project: project.path)

    def get_all_project_names(self):
        """Return all project names"""
        project_names = []
        for project in self.projects:
            project_names.append(project.name)
        return project_names

    def get_yaml(self):
        """Return python object representation for saving yaml"""
        projects_yaml = []
        for project in self.projects:
            projects_yaml.append(project.get_yaml())
        return {'name': self.name, 'projects': projects_yaml}

    def groom(self):
        """Discard changes for all projects"""
        if self.is_dirty():
            print_group(self.name)
            for project in self.projects:
                project.groom()

    def is_dirty(self):
        """Check if group has dirty project(s)"""
        is_dirty = False
        for project in self.projects:
            if project.is_dirty():
                is_dirty = True
        return is_dirty

    def stash(self):
        """Stash changes for all projects with changes"""
        if self.is_dirty():
            print_group(self.name)
            for project in self.projects:
                project.stash()
