# -*- coding: utf-8 -*-

import UserDict
import numpy as np
import ujson as json
import shutil
import os
import hashlib


class NumpyDB(UserDict.DictMixin):
    def __init__(self, prefix):
        self.__prefix__ = prefix
        try:
            os.makedirs(self.__prefix__)
        except Exception:
            pass

        self.__metadata__ = '{0}/metadata.json'.format(self.__prefix__)
        try:
            self.__index__ = json.load(open(self.__metadata__))
        except:
            self.__index__ = []


    def __dir__(self, key):
        h = hashlib.md5(key).hexdigest()
        d = os.path.join(self.__prefix__, *map(''.join, zip(*[iter(h)]*8)))
        return d, h


    def __getitem__(self, key):
        d, h = self.__dir__(key)
        try:
            return np.load('{0}/{1}.npy'.format(d, h))
        except:
            if key in self.__index__:
                self.__index__.remove(key)
                json.dumps(self.__index__, open(self.__metadata__, 'w'))
            return None


    def __setitem__(self, key, value):
        d, h = self.__dir__(key)
        try:
            os.makedirs(d, mode=0755)
        except Exception:
            pass

        try:
            np.save('{0}/{1}.npy'.format(d, h), value)
            self.__index__.append(key)
            json.dumps(self.__index__, open(self.__metadata__, 'w'))
        except Exception:
            raise


    def iterkeys(self):
        for key in self.__index__:
            yield key


    def itervalues(self):
        for key in self.__index__:
            yield self[key]


    def iteritems(self):
        for key in self.__index__:
            yield key, self[key]


    def __iter__(self):
        return self.iterkeys()


    def keys(self):
        return self.__index__


    def values(self):
        return [self[key] for key in self.__index__]


    def items(self):
        return [(key, self[key]) for key in self.__index__]

