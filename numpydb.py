# -*- coding: utf-8 -*-

import UserDict
import numpy as np
import anydbm


class NumpyDB(UserDict.DictMixin):
    def __init__(self, filename, flag='c'):
        self.db = anydbm.open(filename, flag)

    def __getitem__(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        value = self.db.get(key)
        if value:
            return self.unpack(value)

    def __setitem__(self, key, value):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        self.db[key] = self.pack(value)

    def __delitem__(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        del self.db[key]

    def pack(self, s):
        return '-||-'.join([str(s.dtype), str(s.shape), s.tostring()])

    def unpack(self, s):
        dtype, shape, array = s.split('-||-')
        data = np.fromstring(array, dtype=dtype)
        data.shape = eval(shape)
        return data

    def setdefault(self, key, default=None):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        value = self.db.get(key)
        if value:
            return self.unpack(data)
        else:
            if default.any():
                self[key] = default
                return default

    def iterkeys(self):
        for key in self.db:
            yield key.decode('utf-8')

    def itervalues(self):
        for key in self.db:
            yield self[key]

    def iteritems(self):
        for key in self.db:
            yield key.decode('utf-8'), self[key]

    def keys(self):
        return [key.decode('utf-8') for key in self.iterkeys()]

    def values(self):
        return [value for value in self.itervalues()]

    def items(self):
        return [(key.decode('utf-8'), value) for (key, value) in self.iteritems()]

