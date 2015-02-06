# -*- coding: utf-8 -*-

import UserDict
import sqlite3
import logging

class SQLiteDict(UserDict.DictMixin):

    # supported types: int, long, float, str, unicode

    def __init__(self, keytype, valtype, path=':memory:', tablename='Dict'):
        self._keytype, self._valtype = keytype, valtype
        self._con = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        self._cur = self._con.cursor()
        try:
            self._cur.execute('CREATE TABLE {0} (key UNIQUE, value)'.format(tablename))
            self._cur.execute('PRAGMA synchronous=OFF')
            self._cur.execute('PRAGMA count_changes=OFF')
            self._cur.execute('PRAGMA journal_mode=MEMORY')
            self._cur.execute('PRAGMA temp_store=MEMORY')
        except sqlite3.OperationalError:
            pass
        self._insertQuery = 'REPLACE INTO {0} (key, value) values (?, ?)'.format(tablename)
        self._selectQuery = 'SELECT value FROM {0} WHERE key=?'.format(tablename)
        self._selectKeysQuery = 'SELECT key FROM {0}'.format(tablename)
        self._deleteQuery = 'DELETE FROM {0} WHERE key=?'.format(tablename)

    def keys(self):
        self._cur.execute(self._selectKeysQuery)
        return [self._keytype(t[0]) for t in self._cur.fetchall()]

    def batch_insert(self, data):
        adapted = []
        c = 0
        for key, val in data:
            t = []
            for obj, protocol in (key, self._keytype), (val, self._valtype):
                t.append(_generic_adapt(obj, protocol))
            adapted.append(tuple(t))
            if c % 100000 == 0:
                logging.info('Adapted {0} entries.'.format(c))
            c += 1
        logging.info('Adapted {0} entries.'.format(c))
        self._cur.executemany(self._insertQuery, adapted)
        self._con.commit()
        logging.info('Inserted {0} entries.'.format(c))

    def __setitem__(self, key, val):
        adapted = []
        for obj, protocol in (key, self._keytype), (val, self._valtype):
            adapted.append(_generic_adapt(obj, protocol))
        self._cur.execute(self._insertQuery, adapted)

    def __getitem__(self, key):
        self._cur.execute(self._selectQuery, (key,))
        result = self._cur.fetchall()
        if len(result) == 1:
            return self._valtype(result[0][0])
        raise KeyError(str(key))

    def __delitem__(self, key):
        self._cur.execute(self._deleteQuery, (key,))

    def close(self):
        self._con.commit()
        self._cur.close()
        self._con.close()

    def dump(self):
        self._cur.execute('PRAGMA table_info(Dict)')
        return self._cur.fetchall()


def _generic_adapt(obj, protocol):
    try:
        adapted = protocol(obj)
        if adapted == obj:
            return adapted
    except:
        pass
    raise TypeError('%r can not be adapted to %s' %(obj, protocol))


