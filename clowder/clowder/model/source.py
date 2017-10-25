"""Representation of clowder.yaml source"""


class Source(object):
    """clowder.yaml source class"""

    def __init__(self, source):
        self.name = source['name']
        self.url = source['url']

    def get_yaml(self):
        """Return python object representation for saving yaml"""

        return {'name': self.name, 'url': self.url}
