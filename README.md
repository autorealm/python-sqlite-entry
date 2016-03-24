# python-sqlite-entry
非常方便使用的 SQLite 键值对存储数据库类

##如何使用

###首先根据包位置引入库文件
```python

from db import *

```
###可以在公共库文件中定义一个对象转字典类型的函数
```python
def object2dict(obj, accept=False):
    #convert object to a dict
    d = {}
    try:
        d.update(obj.__dict__)
    except StandardError, e:
        if accept: d = obj
        else: d = None
        pass
    return d

```
###调用库之前可以先初始化，传入一个存储位置和名称
```python
init_db(name='sample')
```
###接着就开始使用了~
```python
# 获得一个 Entry，默认返回的是值
value = get_entry(key)

# 设置 Entry，注意由于是键值对存储方式，Key 要是唯一的，默认会覆盖重复的健。这里还可以传入 expire 指定过期时间(单位:秒，0表示不过期)
entry = put_entry(key, value, expire=0)
entry = object2dict(entry)

# 删除一个 Entry
result = delete_entry(key)

# 查询 Entry，返回列表，可以传入 date 日期，tag 标签：进行模糊查询，limit：限制查询行数。
rows = list_entry(tag='')

# 使用后关闭数据库
close_db()
```
