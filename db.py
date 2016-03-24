# -*- coding: utf-8 -*-

import os, sys, time, json, hashlib, base64
reload(sys)
sys.setdefaultencoding('utf8')
from datetime import datetime
from sqlite3 import dbapi2 as sqlite3
try:
    import cPickle as pickle
except ImportError:
    import pickle

sqlite_db = None
db_path = './data.db'


def init_db(name='data'):
    global db_path
    db_path = os.path.join(os.path.dirname(db_path), name + '.db')
    return get_db()

def get_db():
    global sqlite_db
    global db_path
    path = db_path
    if sqlite_db == None:
        try:
            sqlite_db = sqlite3.connect(path)
        except Exception, e:
            pass
        sqlite_db.row_factory = sqlite3.Row
        #sqlite_db.text_factory = sqlite3.OptimizedUnicode
        sqlite_db.text_factory = str
    db = sqlite_db
    if (os.path.isfile(path) and os.path.getsize(path) > 0):
        return db
    with file('schema.sql', mode='r') as f:
        sql = f.read().encode('utf-8')
        db.cursor().executescript(sql)
    db.commit()
    return db


def close_db():
    global sqlite_db
    if sqlite_db:
        sqlite_db.close()
        sqlite_db = None


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    return (rv[0] if rv else None) if one else rv


def gen_random_key(num=16):
    return ''.join(map(lambda xx:(hex(ord(xx))[2:]),os.urandom(num)))


def _pack(date):
    try:
        return json.dumps(date, ensure_ascii=False)
    except Exception, e:
        pass
    try:
        return pickle.dumps(date)
    except Exception, e:
        pass
    return date

def _unpack(date):
    try:
        return json.loads(date)
    except Exception, e:
        pass
    try:
        return pickle.loads(date)
    except Exception, e:
        pass
    return date


# Entry 数据查询

def list_entry(date=None, tag=None, limit=100):
    db = get_db()
    if date == None:
        if tag == None:
            cur = db.execute('select * from entries order by _id desc limit :limit ', {'limit': limit})
        else:
            cur = db.execute("select * from entries where _tags like :tag  order by _id desc \
                            limit :limit ", {"tag": '%'+tag+'%', 'limit': limit})
    else:
        if tag == None:
            cur = db.execute("select * from entries where date(_time)=date(:date) order by _id desc \
                            limit :limit ", {"date": date, 'limit': limit})
        else:
            cur = db.execute("select * from entries where date(_time)=date(:date) and _tags like :tag \
                            order by _id desc limit :limit ", {"tag": '%'+tag+'%', "date": date, 'limit': limit})
    
    rows = cur.fetchall()
    cur.close()
    if rows == None:
        return None
    entries = []
    for row in rows:
        entry = {}
        for index, val in enumerate(row):
            k = row.keys()[index]
            if k=='_value': val = _unpack(val)
            entry[k.strip('_')] = val
        entries.append(entry)
    
    return entries

def get_entry(key, only_value=True):
    db = get_db()
    cur = db.cursor()
    cur.execute("select * from entries where _key=:key", {"key": key})
    row = cur.fetchone()
    cur.close()
    if not row:
        return None
    entry = Entry()
    for index,val in enumerate(row):
        k = row.keys()[index]
        if k=='_value' and only_value==False: val = _unpack(val)
        setattr(entry, k.strip('_'), val)
    if only_value==True:
        if int(entry.expire)==0:
            return _unpack(entry.value)
        elif (int(entry.expire)<(time.time()-long(entry.time))):
            delete_entry(key)
            return None
        else:
            return _unpack(entry.value)
    return entry

def has_entry(key):
    db = get_db()
    cur = db.cursor()
    cur.execute("select * from entries where _key=:key", {"key": key})
    row = cur.fetchall()
    #print cur.rowcount
    cur.close()
    return len(row)

def has_tag(key, tag):
    db = get_db()
    cur = db.cursor()
    cur.execute("select * from entries where _key=:key and _tags like :tag", {"key": key, "tag": '%'+tag+'%'})
    row = cur.fetchall()
    #print cur.rowcount
    cur.close()
    return len(row)

def delete_entry(key):
    db = get_db()
    cur = db.execute("delete from entries where _key=:key", {"key": key})
    #db.rollback();
    db.commit()
    return True

def put_entry(key, value, expire=0, tags=None, overwrite=True):
    db = get_db()
    timestamp = int(time.time())
    size = sys.getsizeof(value, 0)
    value = _pack(value)
    if (has_entry(key) != 0):
        if overwrite==True:
            db.execute('update entries set _value=?, _size=?, _time=?, _expire=?, _tags=? where _key=?',
                       (value, size, timestamp, expire, tags, key))
        else:
            return False
    else:
        db.execute('insert into entries (_key, _value, _size, _time, _expire, _tags) values (?, ?, ?, ?, ?, ?)',
                   [key, value, size, timestamp, expire, tags])
    db.commit()
    return get_entry(key, False)


class Entry(object):
    pass


if __name__ == '__main__':
    from optparse import OptionParser
    opar = OptionParser()
    opar.add_option("-t", "--dbname", type="str", dest="dbname", default=None, help="database name")
    opar.add_option("-q", "--query", type="str", dest="query", default=None, help="query string")
    (opts, args) = opar.parse_args()
    print opts
    if (opts.dbname != None): init_db(opts.dbname)
    rows = list_entry(tag=opts.query)
    print rows
    