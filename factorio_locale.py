import chardet
from configparser import RawConfigParser


class FactorioLocale:
    def __init__(self):
        self.conf = RawConfigParser()
        self.crap = RawConfigParser()

    def get_name(self, section, name):
        return self.conf.get(section, name) or '#%s#%s#' % (section, name)

    def load(self, csv):
        conf = RawConfigParser()
        with open(csv, 'rb') as f:
            input_bytes = f.read()
            decoded = input_bytes.decode(chardet.detect(input_bytes)['encoding'])
            decoded = '[__global__]\n' + decoded
            conf.read_string(decoded)

        for sec in conf.sections():
            if not self.conf.has_section(sec):
                self.conf.add_section(sec)
                self.crap.add_section(sec)

            for k, v in conf.items(sec):
                is_crap = False

                if '__' in v:
                    is_crap = True

                if not is_crap:
                    if self.conf.has_option(sec, k):
                        if self.conf.get(sec, k).lower() != v.lower():
                            print('Overwriting locale %s (%r -> %r)' % (k, self.conf.get(sec, k), v))

                    self.conf.set(sec, k, v)
                else:
                    if self.crap.has_option(sec, k):
                        print('Overwriting crap locale %s (%r -> %r)' % (k, self.crap.get(sec, k), v))

                    self.crap.set(sec, k, v)

    def merge(self):
        for sec in self.crap.sections():
            for k, v in self.crap.items(sec):
                if not self.conf.has_option(sec, k):
                    print('Using crap locale %s (%r)' % (k, v))
                    self.conf.set(sec, k, v)

    def save(self, out):
        with open(out, 'w') as f:
            self.conf.write(f)
