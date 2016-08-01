from collections import OrderedDict
import json
import os

from factorio_locale import FactorioLocale
from factorio_lua import FactorioState
from factorio_pack import PackConfig, PackInfo
from util import mkdir_p


def get_pack_dir(packid):
    return 'pack/%s' % packid


def sort_dict(data, key):
    obj = data[key]
    data[key] = OrderedDict()

    for k in sorted(obj):
        data[key][k] = obj[k]


def load_pack(pack_config: PackConfig):
    if pack_config.mods_path is None:
        pack_config.mods_path = os.path.join(pack_config.factorio_path, 'mods')

    locale = FactorioLocale()
    pack_dir = get_pack_dir(pack_config.name)
    oldcwd = os.getcwd()

    try:
        fs = FactorioState(pack_config.factorio_path, locale)

        for fn in os.listdir(pack_config.mods_path):
            fn = os.path.join(pack_config.mods_path, fn)
            if os.path.isdir(fn):
                fs.modlist.add_mod(fn)

        fs.modlist.resolve()
        fs.load_mods()

        locale.merge()
        data = fs.get_data()
    finally:
        os.chdir(oldcwd)

    mkdir_p(pack_dir)

    sort_dict(data, 'technology')

    with open('%s/out' % pack_dir, 'w') as f:
        f.write(json.dumps(data, indent=4))

    fs.save_gfx('%s/icon' % pack_dir)
    locale.save('%s/localedump.cfg' % pack_dir)

    pack_info = PackInfo(pack_config.name, pack_config.title, '', fs.modlist)

    with open('%s/info.json' % pack_dir, 'w') as f:
        f.write(pack_info.to_json())


if __name__ == '__main__':
    with open('pack_config.json', 'r') as f:
        for pack_conf in json.load(f):
            load_pack(PackConfig(pack_conf))
