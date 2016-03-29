drop table if exists records;
create table records (
  id integer primary key autoincrement,
  time_stamp text,
  device_ID text not null,
  team_code text not null,
  team_name text not null,
  device_reading text not null
);
