import json


class Mod:
    def __init__(self, path):
        self.path = path

        with open('%s/info.json' % self.path, 'r') as f:
            d = f.read().replace('\n', '').replace('\r', '')
            self.info = json.loads(d)

        self.version = self.info['version']
        self.dependencies = [s.strip().split(' ') for s in
                             self.info['dependencies']] if 'dependencies' in self.info else []
        self.name = self.info['name']
        self.title = self.info['title']
        self.description = self.info['description']

    def __repr__(self):
        return 'Mod(title=%r, dependencies=%r, name=%r, version=%r)' % (
            self.title, self.dependencies, self.name, self.version)
