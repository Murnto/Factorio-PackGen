import os
import shutil

from lupa import LuaRuntime

from factorio_locale import FactorioLocale
from factorio_modlist import FactorioModList
from util import mkdir_p


class FactorioState(object):
    LUA_LIBS = ['util', 'dataloader', 'autoplace_utils', 'story', 'defines']

    def __init__(self, factorio_path, locale: FactorioLocale):
        super(FactorioState, self).__init__()
        self.factorio_path = factorio_path
        self.locale = locale
        self.lua = LuaRuntime(unpack_returned_tuples=True)

        self.lua.execute("""
local old_require = require
function require (module)
    local ok, m = pcall (old_require, module)
    -- if ok then
        return m
    -- end
    -- try getting module from internal strings
end
        """)
        self.modlist = FactorioModList()

        self._load_libs(self.lua)
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

    def _load_libs(self, lua):
        lib_dir = '%s/data/core/lualib/' % self.factorio_path
        for lib in FactorioState.LUA_LIBS:
            FactorioState.require(lua, lib_dir, lib)
        FactorioState.require(lua, '%s/data/core' % self.factorio_path, 'data')

    @staticmethod
    def require(lua, path, module):
        os.chdir(path)
        if not lua.require(module):
            raise RuntimeError('Require failed: %s in %s' % (module, path))

    def get_data(self):
        return FactorioState.table_to_dict(self.lua.globals()['data']['raw'])

    def load_mods(self):
        # load locale
        for mod in self.modlist.mod_order:
            locale_dir = '%s/locale/en/' % mod.path
            if os.path.exists(locale_dir):
                for fn in os.listdir(locale_dir):
                    fn = os.path.join(locale_dir, fn)
                    if os.path.isfile(fn) and fn.endswith('.cfg'):
                        self.locale.load(fn)

        for mod in self.modlist.mod_order:
            print('Load %s' % mod.title)
            if os.path.exists(os.path.join(mod.path, 'data.lua')):
                self.load_mod(mod.path, 'data')

        for mod in self.modlist.mod_order:
            print('Load %s' % mod.title)
            if os.path.exists(os.path.join(mod.path, 'data-updates.lua')):
                self.load_mod(mod.path, 'data-updates')

        for mod in self.modlist.mod_order:
            print('Load %s' % mod.title)
            if os.path.exists(os.path.join(mod.path, 'data-final-fixes.lua')):
                self.load_mod(mod.path, 'data-final-fixes')

    def load_mod(self, path, name):
        important = [u'table', u'io', u'math', u'debug', u'package', u'_G', u'python', u'string', u'os', u'coroutine',
                     u'bit32', u'util', u'autoplace_utils']
        for p in list(self.lua.globals()['package']['loaded']):
            if p not in important:
                del self.lua.globals()['package']['loaded'][p]

        self.require(self.lua, path, name)

    def save_gfx(self, path, data=None):
        if data is None:
            print('got data')
            data = self.get_data()

        for k, v in data.items():
            if type(v) is dict:
                self.save_gfx(path, v)
                pass
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
