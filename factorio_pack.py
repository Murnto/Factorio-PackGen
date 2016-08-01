import json


class PackInfo:
    def __init__(self, name=None, title=None, description=None, mods=None):
        self.name = name
        self.title = title
        self.description = description
        self.mods = []

        for mod in mods.mods:
            self.mods.append({
                'version': mod.version,
                'name': mod.name,
                'title': mod.title,
                'description': mod.description,
            })

    def to_json(self):
        return json.dumps(self.__dict__, indent=4)


class PackConfig:
    def __init__(self, config: dict):
        self.name = None
        self.title = None
        self.factorio_path = None
        self.mods_path = None

        self.__dict__.update(config)
