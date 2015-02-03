# -*- coding: utf-8 -*-

import UserDict
import numpy as np
import ujson
import shutil
import os
import hashlib


class NumpyDB(UserDict.DictMixin):
    def __init__(self, prefix):
        self.__prefix__ = prefix
        try:
            os.makedirs(self.__prefix__)
        except:
            pass

        self.__metadata__ = '{0}/metadata.json'.format(self.__prefix__)
        try:
            self.__index__ = ujson.load(open(self.__metadata__))
        except:
            self.__index__ = []


    def __dir__(self, key):
        h = hashlib.md5(key).hexdigest()
        d = os.path.join(self.__prefix__, *map(''.join, zip(*[iter(h)]*8)))
        return d


    def __getitem__(self, key):
        p = self.__dir__(key)
        try:
            return np.load('{0}/{1}.npy'.format(p, key))
        except:
            if key in self.__index__:
                self.__index__.remove(key)
                ujson.dumps(self.__index__, open(self.__metadata__, 'w'))
            return None


    def __setitem__(self, key, value):
        p = self.__dir__(key)
        try:
            os.makedirs(p)
        except:
            pass
        np.save('{0}/{1}.npy'.format(p, key), value)
        self.__index__.append(key)
        ujson.dumps(self.__index__, open(self.__metadata__, 'w'))


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

