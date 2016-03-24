drop table if exists entries;
create table entries (
  _id integer primary key autoincrement,
  _key text not null unique,
  _value text not null,
  _expire integer default 0,
  _size integer default 0,
  _time timestamp default CURRENT_TIMESTAMP,
  _tags text default null
);

create index key_idx on entries(_key);
create index tag_idx on entries(_tags);
