import sqlite3
from .sql_db_helper import DBHelper


def create_sensor_table(dbHelper):
    '''
    pressure: 0-1023
    gyro: 0-180
    distance: 3-350
    '''

    sql = '''
    CREATE TABLE sensor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        devicename CHAR(5) NOT NULL,
        pressure VARCHAR(4) NOT NULL,
        gyro VARCHAR(3) NOT NULL,
        leftdistance VARCHAR(4) NOT NULL,
        rightdistance VARCHAR(4) NOT NULL,
        temperature VARCHAR(4) NOT NULL,
        image BLOB NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        is_flipped INTEGER DEFAULT -1 NOT NULL,
        is_flipped_prob INTEGER DEFAULT -1 NOT NULL,
        is_eye_open INTEGER DEFAULT -1 NOT NULL,
        is_relayed INTEGER DEFAULT 0 NOT NULL
    );
    '''
    dbHelper.execute(sql)

def drop_table(dbHelper):
    sql = '''
    DROP TABLE IF EXISTS sensor
    '''
    dbHelper.execute(sql)


def create_alarm_table(dbHelper):
    sql = '''
    CREATE TABLE alarm_event (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        devicename CHAR(5) NOT NULL,
        timestamp TIMESTAMP NOT NULL,
        interval_start TIMESTAMP NOT NULL,
        interval_end TIMESTAMP NOT NULL,
        sensor_data_count INTEGER NOT NULL,
        flipped_count INTEGER NOT NULL,
        ratio INTEGER NOT NULL,
        threshold INTEGER NOT NULL
    );
    '''
    dbHelper.execute(sql)


def create_config_table(dbHelper):
    sql = '''
    CREATE TABLE config (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR UNIQUE NOT NULL,
        config JSON NOT NULL
    );
    '''
    dbHelper.execute(sql)


def create_user_table(dbHelper):
    sql = '''
    CREATE TABLE user (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        username VARCHAR UNIQUE NOT NULL,
        salt VARCHAR NOT NULL,
        password VARCHAR NOT NULL
    );
    '''
    dbHelper.execute(sql)


def create_baby_table(dbHelper):
    sql = '''
    CREATE TABLE baby_profile (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name VARCHAR NOT NULL,
        last_name VARCHAR NOT NULL,
        age INTEGER NOT NULL,
        height FLOAT NOT NULL,
        weight FLOAT NOT NULL,
        image BLOB,
        user_id INTEGER NOT NULL,
        devicename VARCHAR NOT NULL,
        FOREIGN KEY (user_id) REFERENCES user(id)
    );
    '''
    dbHelper.execute(sql)
