import os
import shutil
from collections import OrderedDict
import sys
orig_dlflags = sys.getdlopenflags()
sys.setdlopenflags(258)
from lupa import LuaRuntime
sys.setdlopenflags(orig_dlflags)

from factorio_locale import FactorioLocale
from factorio_modlist import FactorioModList
from util import mkdir_p


class FactorioState(object):
    LUA_LIBS = ['util', 'dataloader', 'autoplace_utils', 'story', 'defines']

    def __init__(self, factorio_path, locale: FactorioLocale):
        super(FactorioState, self).__init__()
        self.factorio_path = factorio_path
        self.locale = locale
        self.data = None

        self.modlist = FactorioModList()

        self.modlist.add_mod('%s/data/base/' % self.factorio_path)

    @staticmethod
    def table_to_dict(tab):
        tab_type = type(tab)
        ret = {}
        for k, v in tab.items():
            if type(v) is tab_type:
                ret[k] = FactorioState.table_to_dict(v)
            else:
                ret[k] = v
        return ret

    @staticmethod
    def require(lua, path, module):
        os.chdir(path)
        if not lua.require(module):
            raise RuntimeError('Require failed: %s in %s' % (module, path))

    def get_data(self):
        return self.data

    def load_mods(self):
        # load locale
        for mod in self.modlist.mod_order:
            locale_dir = '%s/locale/en/' % mod.path
            if os.path.exists(locale_dir):
                for fn in os.listdir(locale_dir):
                    fn = os.path.join(locale_dir, fn)
                    if os.path.isfile(fn) and fn.endswith('.cfg'):
                        self.locale.load(fn)

        old = os.path.abspath(os.curdir)
        os.chdir('factorio-lua-tools')

        lua = LuaRuntime(unpack_returned_tuples=True)
        loader = lua.require('loader')

        # TODO this is awful
        lua.execute('defines = {}')
        lua.execute('defines.difficulty_settings = {}')
        lua.execute('defines.difficulty_settings.recipe_difficulty = {}')
        lua.execute('defines.difficulty_settings.recipe_difficulty.normal = 1')
        lua.execute('defines.difficulty_settings.recipe_difficulty.expensive = 2')
        lua.execute('defines.difficulty_settings.technology_difficulty = {}')
        lua.execute('defines.difficulty_settings.technology_difficulty.normal = 1')
        lua.execute('defines.difficulty_settings.technology_difficulty.expensive = 2')
        lua.execute('defines.direction = {}')
        lua.execute('defines.direction.north = 0')
        lua.execute('defines.direction.east = 1')
        lua.execute('defines.direction.south = 2')
        lua.execute('defines.direction.west = 3')
        lua.execute('function log(x) end')

        core_path = '%s/data/core/' % self.factorio_path
        mod_paths = [mod.path for mod in self.modlist.mod_order]

        loader.load_data(lua.table_from([core_path] + mod_paths))

        os.chdir(old)

        self.data = FactorioState.table_to_dict(loader.data)

    def save_gfx(self, path, data=None):
        if data is None:
            print('got data')
            data = self.get_data()

        for k, v in data.items():
            if type(v) is dict or type(v) is OrderedDict:
                self.save_gfx(path, v)
            elif k == 'icon':
                icon_path = data['icon'].split('/')

                if icon_path[0] not in self.modlist.path_map:
                    print('Unknown content path %s for %s/%s' % (icon_path[0], data['type'], data['name']))
                    continue

                icon_path[0] = self.modlist.path_map[icon_path[0]]
                icon_path = '/'.join(icon_path)

                if 'type' not in data:
                    # attempt to extract name and type from filepath
                    path_els = v[:v.rindex('.')].split('/')
                    itm_type, name = path_els[-2:]
                else:
                    itm_type, name = data['type'], data['name']

                out_dir = '%s/%s' % (path, itm_type)
                out_path = '%s/%s.png' % (out_dir, name)
                mkdir_p(out_dir)

                if os.path.exists(out_path):
                    print('Overwriting %s/%s' % (itm_type, name))

                shutil.copy2(icon_path, out_path)
