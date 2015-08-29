"""Model representation of clowder.yaml remote"""

class Remote(object):
    """Model class for clowder.yaml remote"""

    def __init__(self, remote):
        self.name = remote['name']
        self.url = remote['url']

    def get_yaml(self):
        """Return python object representation for saving yaml"""
        return {'name': self.name, 'url': self.url}