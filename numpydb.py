# -*- coding: utf-8 -*-

import UserDict
import numpy as np
import ujson as json
import os
import hashlib


class NumpyDB(UserDict.DictMixin):
    def __init__(self, prefix, sync=True):
        self.sync = sync
        self.prefix = prefix
        try:
            os.makedirs(self.prefix)
        except Exception:
            pass

        self.metadata = '{0}/metadata.json'.format(self.prefix)
        try:
            self.index = json.load(open(self.metadata))
        except:
            self.index = []


    def __dir__(self, key):
        h = hashlib.md5(key).hexdigest()
        d = os.path.join(self.prefix, *map(''.join, zip(*[iter(h)]*8)))
        return d, h


    def __getitem__(self, key):
        d, h = self.__dir__(key)
        try:
            return np.load('{0}/{1}.npy'.format(d, h))
        except:
            if key in self.index:
                self.index.remove(key)
                json.dump(self.index, open(self.metadata, 'w'))
            return None


    def __setitem__(self, key, value):
        d, h = self.__dir__(key)
        try:
            os.makedirs(d, mode=0755)
        except Exception:
            pass

        try:
            np.save('{0}/{1}.npy'.format(d, h), value)
            self.index.append(key)
            if self.sync:
                self.save_metadata()
        except Exception:
            raise


    def save_metadata(self):
        json.dump(self.index, open(self.metadata, 'w'))


    def iterkeys(self):
        for key in self.index:
            yield key


    def itervalues(self):
        for key in self.index:
            yield self[key]


    def iteritems(self):
        for key in self.index:
            yield key, self[key]


    def __iter__(self):
        return self.iterkeys()


    def keys(self):
        return self.index


    def values(self):
        return [self[key] for key in self.index]


    def items(self):
        return [(key, self[key]) for key in self.index]

