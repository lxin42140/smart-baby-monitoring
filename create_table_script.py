from db.sql_db_helper import DBHelper
from db.util import *

dbHelper = DBHelper(db_name='cloud.db')
create_sensor_table(dbHelper)
create_alarm_table(dbHelper)
create_config_table(dbHelper)
create_user_table(dbHelper)
create_baby_table(dbHelper)

dbHelper = DBHelper(db_name='fog.db')
create_sensor_table(dbHelper)
