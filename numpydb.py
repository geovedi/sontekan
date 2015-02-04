# -*- coding: utf-8 -*-

import UserDict
import numpy as np
import plyvel


class NumpyDB(UserDict.DictMixin):
    def __init__(self, filename, create_if_missing=True, sync=True):
        self.db = plyvel.DB(filename, create_if_missing=create_if_missing)
        self.sync = sync

    def __getitem__(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        try:
            return self.unpack(self.db.get(key))
        except Exception:
            return None

    def __setitem__(self, key, value):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        self.db.put(key, self.pack(value), sync=self.sync)

    def __delitem__(self, key):
        if isinstance(key, unicode):
            key = key.encode('utf-8')
        self.db.delete(key, sync=self.sync)

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
        try:
            return self.unpack(self.db.get(key))
        except Exception:
            if default.any():
                self[key] = default
                return default
            return None

    def write_batch(self, *args, **kwargs):
        return self.db.write_batch(*args, **kwargs)

    def close(self):
        self.db.close()

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
