# -*- coding: utf-8 -*-
#
# Modified Radim Řehůřek's sqlitedict to use generic supported types.

import sqlite3
import logging

from threading import Thread
from sys import version_info

_major_version = version_info[0]
if _major_version < 3:
  if version_info[1] < 5:
    raise ImportError("sqlitedict requires python 2.5 or higher (python 3.3 or higher supported)")

try:
   from collections import UserDict as DictClass
except ImportError:
   from UserDict import DictMixin as DictClass

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

logger = logging.getLogger(__name__)


def open(*args, **kwargs):
    return SqliteDict(*args, **kwargs)


def encode(obj, obj_type):
    try:
        adapted = obj_type(obj)
        if adapted == obj:
            return adapted
    except:
        pass
    raise TypeError('%r can not be adapted to %s' %(obj, obj_type))


class SqliteDict(DictClass):
    """
    Supported types: int, long, float, str, unicode
    
    """
    def __init__(self, key_type=unicode, value_type=int, filename=':memory:', tablename='Dict', autocommit=False, journal_mode='DELETE'):
        self._key_type, self._value_type = key_type, value_type
        self.filename, self.tablename = filename, tablename

        logger.info("opening Sqlite table %r in %s" % (tablename, filename))
        self.conn = SqliteMultithread(filename, autocommit=autocommit, journal_mode=journal_mode)
        MAKE_TABLE = 'CREATE TABLE IF NOT EXISTS %s (key TEXT PRIMARY KEY, value BLOB)' % self.tablename
        self.conn.execute(MAKE_TABLE)
        self.conn.commit()

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()

    def __str__(self):
        return "SqliteDict(%s)" % (self.conn.filename)

    def __repr__(self):
        return str(self)

    def __len__(self):
        GET_LEN = 'SELECT COUNT(*) FROM %s' % self.tablename
        rows = self.conn.select_one(GET_LEN)[0]
        return rows if rows is not None else 0

    def __bool__(self):
        GET_MAX = 'SELECT MAX(ROWID) FROM %s' % self.tablename
        m = self.conn.select_one(GET_MAX)[0]
        return True if m is not None else False


    def keys(self):
        GET_KEYS = 'SELECT key FROM %s ORDER BY rowid' % self.tablename
        return [encode(key[0], self._key_type) for key in self.conn.select(GET_KEYS)]

    def values(self):
        GET_VALUES = 'SELECT value FROM %s ORDER BY rowid' % self.tablename
        return  [encode(value[0], self._value_type) for value in self.conn.select(GET_VALUES)]

    def items(self):
        GET_ITEMS = 'SELECT key, value FROM %s ORDER BY rowid' % self.tablename
        return [(encode(key, self._key_type), encode(value, self._value_type))
                for key, value in self.conn.select(GET_ITEMS)]

    def __contains__(self, key):
        HAS_ITEM = 'SELECT 1 FROM %s WHERE key = ?' % self.tablename
        return self.conn.select_one(HAS_ITEM, (key,)) is not None

    def __getitem__(self, key):
        GET_ITEM = 'SELECT value FROM %s WHERE key = ?' % self.tablename
        item = self.conn.select_one(GET_ITEM, (key,))
        if item is None:
            raise KeyError(key)
        return encode(item[0], self._value_type)

    def __setitem__(self, key, value):
        ADD_ITEM = 'REPLACE INTO %s (key, value) VALUES (?,?)' % self.tablename
        self.conn.execute(ADD_ITEM, (encode(key, self._key_type), encode(value, self._value_type)))

    def __delitem__(self, key):
        if key not in self:
            raise KeyError(key)
        DEL_ITEM = 'DELETE FROM %s WHERE key = ?' % self.tablename
        self.conn.execute(DEL_ITEM, (key,))

    def update(self, items=(), **kwds):
        try:
            items = [(encode(k, self._key_type), encode(v, self._value_type)) for k, v in items.items()]
        except AttributeError:
            pass

        UPDATE_ITEMS = 'REPLACE INTO %s (key, value) VALUES (?, ?)' % self.tablename
        self.conn.executemany(UPDATE_ITEMS, items)
        if kwds:
            self.update(kwds)

    def __iter__(self):
        return iter(self.keys())

    def clear(self):
        CLEAR_ALL = 'DELETE FROM %s;' % self.tablename
        self.conn.commit()
        self.conn.execute(CLEAR_ALL)
        self.conn.commit()

    def commit(self):
        if self.conn is not None:
            self.conn.commit()
    sync = commit

    def close(self):
        logger.debug("closing %s" % self)
        if self.conn is not None:
            if self.conn.autocommit:
                self.conn.commit()
            self.conn.close()
            self.conn = None
        if self.in_temp:
            try:
                os.remove(self.filename)
            except:
                pass

    def terminate(self):
        self.close()

        if self.filename == ':memory:':
            return

        logger.info("deleting %s" % self.filename)
        try:
            os.remove(self.filename)
        except IOError:
            _, e, _ = sys.exc_info()
            logger.warning("failed to delete %s: %s" % (self.filename, str(e)))

    def __del__(self):
        try:
            if self.conn is not None:
                if self.conn.autocommit:
                    self.conn.commit()
                self.conn.close()
                self.conn = None
            if self.in_temp:
                os.remove(self.filename)
        except:
            pass

if _major_version == 2:
    setattr(SqliteDict, "iterkeys", lambda self: self.keys())
    setattr(SqliteDict, "itervalues", lambda self: self.values())
    setattr(SqliteDict, "iteritems", lambda self: self.items())
    SqliteDict.__nonzero__ = SqliteDict.__bool__
    del SqliteDict.__bool__



class SqliteMultithread(Thread):
    def __init__(self, filename, autocommit, journal_mode):
        super(SqliteMultithread, self).__init__()
        self.filename = filename
        self.autocommit = autocommit
        self.journal_mode = journal_mode
        self.reqs = Queue()
        self.setDaemon(True)
        self.start()

    def run(self):
        if self.autocommit:
            conn = sqlite3.connect(self.filename, isolation_level=None, check_same_thread=False)
        else:
            conn = sqlite3.connect(self.filename, check_same_thread=False)
        conn.execute('PRAGMA journal_mode = %s' % self.journal_mode)
        conn.text_factory = str
        cursor = conn.cursor()
        cursor.execute('PRAGMA synchronous=OFF')
        cursor.execute('PRAGMA count_changes=OFF')
        cursor.execute('PRAGMA temp_store=MEMORY')
        while True:
            req, arg, res = self.reqs.get()
            if req == '--close--':
                break
            elif req == '--commit--':
                conn.commit()
            else:
                cursor.execute(req, arg)
                if res:
                    for rec in cursor:
                        res.put(rec)
                    res.put('--no more--')
                if self.autocommit:
                    conn.commit()
        conn.close()

    def execute(self, req, arg=None, res=None):
        self.reqs.put((req, arg or tuple(), res))

    def executemany(self, req, items):
        for item in items:
            self.execute(req, item)

    def select(self, req, arg=None):
        res = Queue()
        self.execute(req, arg, res)
        while True:
            rec = res.get()
            if rec == '--no more--':
                break
            yield rec

    def select_one(self, req, arg=None):
        try:
            return next(iter(self.select(req, arg)))
        except StopIteration:
            return None

    def commit(self):
        self.execute('--commit--')

    def close(self):
        self.execute('--close--')
        self.join()

