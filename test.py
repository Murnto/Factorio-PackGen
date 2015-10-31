from collections import OrderedDict
import json
import locale
import os

from factorio_lua import FactorioState
from util import mkdir_p


def get_pack_dir(packid):
    return 'pack/%s' % packid


def sort_dict(data, key):
    obj = data[key]
    data[key] = OrderedDict()

    for k in sorted(obj):
        data[key][k] = obj[k]


def load_pack(packid, packtitle, factorio_path, mods_path=None):
    if mods_path is None:
        mods_path = os.path.join(factorio_path, 'mods')

    locale.clear()
    pack_dir = get_pack_dir(packid)
    oldcwd = os.getcwd()

    try:
        fs = FactorioState(factorio_path)

        for fn in os.listdir(mods_path):
            fn = os.path.join(mods_path, fn)
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

    with open('%s/info.json' % pack_dir, 'w') as f:
        f.write("""{
    "name": "%s",
    "version": "%s",
    "title": "%s",
    "description": "",
    "mods": %s
}""" % (packid, '', packtitle, json.dumps(fs.modlist._loaded_names)))


if __name__ == '__main__':
    load_pack('base-f11', 'Base Game F11', '/media/data/factorio/factorio_0.11.22')
    load_pack('base-f12', 'Base Game F12', '/media/data/factorio/factorio_0.12.15')
    load_pack('bobmods-f12', 'Bob\'s mods F12', '/media/data/factorio/factorio_0.12.15',
              '/media/data/factorio/mods/bobmods-f12')
    load_pack('bobmods-f11', 'Bob\'s Mods F11', '/media/data/factorio/factorio_0.11.22',
              '/media/data/factorio/mods/bobmods-f11')

    # load_pack('cartmen-f12', 'Cartmen mods F12', '/media/data/factorio/factorio_0.12.15', '/media/data/factorio/mods/cartmen-f12')

    load_pack('mopack-f11', 'MoMods F11', '/media/data/factorio/factorio_0.11.22',
              '/media/data/factorio/mods/mopack-f11')
    load_pack('mopack-f12', 'MoMods F12', '/media/data/factorio/factorio_0.12.15',
              '/media/data/factorio/mods/mopack-f12')

    load_pack('yuoki-f11', 'Yuoki F11', '/media/data/factorio/factorio_0.11.22',
              '/media/data/factorio/mods/yuoki-f11-0.2.29')  # (0.2.29)
    load_pack('yuoki-f11-a', 'Yuoki F11 w/ addons', '/media/data/factorio/factorio_0.11.22',
              '/media/data/factorio/mods/yuoki-f11-0.2.29-addons')  # (0.2.29)
    load_pack('yuoki-f12', 'Yuoki F12', '/media/data/factorio/factorio_0.12.15',
              '/media/data/factorio/mods/yuoki-f12-0.2.37')  # (0.2.37)
    load_pack('yuoki-f12-a', 'Yuoki F12 w/ addons', '/media/data/factorio/factorio_0.12.15',
              '/media/data/factorio/mods/yuoki-f12-0.2.37-addons')  # (0.2.37)

    load_pack('5dim-f12', '5dim F12', '/media/data/factorio/factorio_0.12.15', '/media/data/factorio/mods/5dim-f12')
    load_pack('5dim-f11', '5dim F11', '/media/data/factorio/factorio_0.11.22', '/media/data/factorio/mods/5dim-f11')

    load_pack('dytech-f11', 'DyTech F11', '/media/data/factorio/factorio_0.11.22',
              '/media/data/factorio/mods/dytech-f11')
    load_pack('dytech-f12', 'DyTech F12', '/media/data/factorio/factorio_0.12.15',
              '/media/data/factorio/mods/dytech-f12')
