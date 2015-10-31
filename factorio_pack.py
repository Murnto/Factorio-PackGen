import json


class PackInfo:
    def __init__(self, name=None, title=None, version=None, description=None, mods=None):
        self.name = name
        self.title = title
        self.version = version
        self.description = description
        self.mods = mods

    def to_json(self):
        return json.dumps(self.__dict__, indent=4)


class PackConfig:
    def __init__(self, config: dict):
        self.name = None
        self.title = None
        self.factorio_path = None
        self.mods_path = None

        self.__dict__.update(config)
