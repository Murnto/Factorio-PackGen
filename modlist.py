from mod import Mod


class ModList(object):
    def __init__(self):
        super(ModList, self).__init__()
        self.mods = []
        self.mod_order = []
        self._loaded_names = []
        self._all_names = []
        self.path_map = {}

    def add_mod(self, path):
        m = Mod(path)
        self.mods.append(m)
        self._all_names.append(m.name)
        self.path_map['__%s__' % m.name] = m.path

    def get_mod_by_name(self, name):
        for m in self.mods:
            if m.name == name:
                return m
        return None

    @staticmethod
    def compare_versions(v1, v2):
        if v1 == v2:
            return 0
        spl1, spl2 = [int(a) for a in v1.split('.')], [int(a) for a in v2.split('.')]
        for i in xrange(len(spl1)):
            if spl1[i] == spl2[i]:
                continue
            if spl1[i] < spl2[i]:
                return 1
            elif spl1[i] > spl2[i]:
                return -1
        if len(spl1) < len(spl2):
            return 1

    def resolve(self):
        left_to_load = list(self.mods)
        last_len = -1

        while len(left_to_load) > 0:
            if last_len == len(left_to_load):
                raise RuntimeError('Not getting anywhere resolving dependencies')

            last_len = len(left_to_load)

            for mod in left_to_load:
                if mod.name in self._loaded_names:
                    left_to_load.remove(mod)
                    continue

                fail = False
                # check dependencies
                for dep in mod.dependencies:
                    optional = dep[0] == '?'
                    if optional:
                        dep = dep[1:]

                    if len(dep[0]) > 0 and dep[0][0] == '?':
                        optional = True
                        dep[0] = dep[0][1:]

                    if optional:
                        if dep[0] not in self._all_names:
                            continue

                    if dep[0] not in self._all_names:
                        raise RuntimeError('Dependency failed! Loading %s, needs unknown mod %s' % (mod.name, dep[0]))

                    if dep[0] not in self._loaded_names:
                        fail = True
                        break

                    if len(dep) == 1:
                        continue

                    dependee = self.get_mod_by_name(dep[0])
                    ver_comp = ModList.compare_versions(dep[2], dependee.version)

                    if dep[1] == u'=':
                        if ver_comp != 0:
                            raise RuntimeError('Dependency failed! Loading %s, needs %s version %s but found %s' % (
                                mod.name, dependee.name, dep[2], dependee.version))
                    elif dep[1] == u'>=':
                        if ver_comp < 0:
                            raise RuntimeError('Dependency failed! Loading %s, needs %s version >= %s but found %s' % (
                                mod.name, dependee.name, dep[2], dependee.version))
                    elif dep[1] == u'>':
                        if ver_comp < 1:
                            raise RuntimeError('Dependency failed! Loading %s, needs %s version > %s but found %s' % (
                                mod.name, dependee.name, dep[2], dependee.version))
                    else:
                        print
                        raise RuntimeError('What is %s?' % dep[1])

                if not fail:
                    # print mod
                    self._loaded_names.append(mod.name)
                    left_to_load.remove(mod)
                    self.mod_order.append(mod)
