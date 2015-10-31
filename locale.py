from configparser import RawConfigParser

_conf, _crap = None, None


def clear():
    global _conf, _crap
    _conf = RawConfigParser()
    _crap = RawConfigParser()


def get_name(section, name):
    return _conf.get(section, name) or '#%s#%s#' % (section, name)


def load(csv):
    conf = RawConfigParser()
    # utf-8-sig per https://bugs.python.org/issue7185#msg94346
    with open(csv, encoding='utf-8-sig') as f:
        conf.read_file(f)

    for sec in conf.sections():
        if not _conf.has_section(sec):
            _conf.add_section(sec)
            _crap.add_section(sec)

        for k, v in conf.items(sec):
            is_crap = False

            if '__' in v:
                is_crap = True

            if not is_crap:
                if _conf.has_option(sec, k):
                    if _conf.get(sec, k).lower() != v.lower():
                        print('Overwriting locale %s (%r -> %r)' % (k, _conf.get(sec, k), v))

                _conf.set(sec, k, v)
            else:
                if _crap.has_option(sec, k):
                    print('Overwriting crap locale %s (%r -> %r)' % (k, _crap.get(sec, k), v))

                _crap.set(sec, k, v)


def merge():
    for sec in _crap.sections():
        for k, v in _crap.items(sec):
            if not _conf.has_option(sec, k):
                print('Using crap locale %s (%r)' % (k, v))
                _conf.set(sec, k, v)


def save(out):
    with open(out, 'w') as f:
        _conf.write(f)
