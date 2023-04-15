from .sql_db_helper import DBHelper
from .models import *


class CloudDBHelper(DBHelper):

    ###################################################
    # sensor
    ###################################################

    def select_all_sensor_data(self) -> list[SensorData]:
        all_sensor_data = self.select('select * from sensor order by id desc;')

        return [SensorData(x) for x in all_sensor_data] if all_sensor_data else []

    def select_sensor_data_for_fog(self, fog_name: str) -> list[SensorData]:
        sql = '''
        select *
        from sensor
        where devicename = '{}'
        order by id desc;
        '''.format(fog_name)

        print("Executing SQL: {}".format(sql))

        all_sensor_data = self.select(sql)

        return [SensorData(x) for x in all_sensor_data] if all_sensor_data else []

    def select_sensor_data_between_interval_for_fog(self, fog_name, start_time, end_time) -> list[SensorData]:
        sql = '''
        select *
        from sensor
        where devicename = '{}'
        and timestamp >= datetime('{}', 'localtime')
        and timestamp <= datetime('{}', 'localtime');
        '''.format(fog_name, start_time, end_time)

        print("Executing SQL: {}".format(sql))

        all_sensor_data = self.select(sql)

        return [] if (all_sensor_data is None or len(all_sensor_data) == 0) else [SensorData(x) for x in all_sensor_data]

    def insert_sensor_data(self, data: dict) -> bool:
        '''
        return true if inserted successfully, else return false
        '''

        sql = "insert into sensor (devicename, pressure, gyro, leftdistance, rightdistance, temperature, image, timestamp, is_flipped, is_flipped_prob, is_eye_open, is_relayed) values (?, ?, ?, ?, ?, ?, ?, datetime(?, 'localtime'), ?, ?, ?, ?);"

        try:
            self.__connect__()
            self.cur.execute(sql, (data["devicename"],
                                   data["pressure"],
                                   data["gyro"],
                                   data["leftdistance"],
                                   data["rightdistance"],
                                   data["temperature"],
                                   data["image"],
                                   data["timestamp"],
                                   data["is_flipped"],
                                   data["is_flipped_prob"],
                                   data["is_eye_open"],
                                   data["is_relayed"])
                             )
            self.con.commit()

            return True
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

            return False

    ###################################################
    # Posture detection
    ###################################################

    def select_count_flipped_by_fog_and_time(self, fog_name, start_time) -> int:
        sql = '''
            select coalesce(count(*), 0)
            from sensor
            where devicename = '{}'
            and is_flipped = 1
            and timestamp >= datetime('{}', 'localtime');
            '''.format(fog_name, start_time)

        print("Executing SQL: {}".format(sql))

        return self.select(sql)[0][0]

    def select_count_by_fog_and_time(self, fog_name, start_time) -> int:
        sql = '''
            select coalesce(count(*), 0)
            from sensor
            where devicename = '{}'
            and timestamp >= datetime('{}', 'localtime');
            '''.format(fog_name, start_time)

        print("Executing SQL: {}".format(sql))

        return self.select(sql)[0][0]

    ###################################################
    # CONFIG
    ###################################################

    def insert_config(self, data) -> bool:
        '''
        return true if inserted successfully, else return false
        '''

        sql = "insert into config ('name', 'config') values(?, ?);"

        try:
            self.__connect__()
            self.cur.execute(sql, (data["name"], json.dumps(data["config"]),))
            self.con.commit()

            return True
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

            return False

    def update_config(self, data: dict) -> None:
        sql = '''
        update config
        set config = '{}'
        where name  = '{}';
        '''.format(json.dumps(data["config"]), data["name"])

        print("Executing SQL: {}".format(sql))

        self.execute(sql)

    def select_config(self, config_name):
        sql = "select * from config where name = '{}';".format(
            config_name)

        print("Executing SQL: {}".format(sql))

        config = self.select(sql)

        return config[0] if config else None

    ###################################################
    # ALARM
    ###################################################

    def insert_alarm_event(self, data) -> bool:
        '''
        return true if inserted successfully, else return false
        '''

        sql = "insert into alarm_event (devicename, timestamp, interval_start, interval_end, sensor_data_count, flipped_count, ratio, threshold) values (?, datetime('now', 'localtime'), ?, ?, ?, ?, ?, ?);"

        try:
            self.__connect__()
            self.cur.execute(sql, (data["devicename"],
                                   data["interval_start"],
                                   data["interval_end"],
                                   data["sensor_data_count"],
                                   data["flipped_count"],
                                   data["ratio"],
                                   data["threshold"])
                             )
            self.con.commit()

            return True
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

            return False

    def select_all_alarm_event(self) -> list[AlarmEvent]:
        sql = '''
        select * 
        from alarm_event
        order by id desc;
        '''

        print("Executing SQL: {}".format(sql))

        all_alarm = self.select(sql)

        return [AlarmEvent(x) for x in all_alarm] if all_alarm else []

    def select_all_alarm_for_fog(self, fog_name: str) -> list[AlarmEvent]:
        sql = '''
        select * 
        from alarm_event
        where devicename = '{}'
        order by id desc;
        '''.format(fog_name)

        print("Executing SQL: {}".format(sql))

        all_alarm = self.select(sql)

        return [AlarmEvent(x) for x in all_alarm] if all_alarm else []

    def select_alarm_between_interval_for_fog(self, fog_name, start_time, end_time) -> list[AlarmEvent]:
        sql = '''
        select *
        from alarm_event
        where devicename = '{}'
        and timestamp >= datetime('{}', 'localtime')
        and timestamp <= datetime('{}', 'localtime');
        '''.format(fog_name, start_time, end_time)

        print("Executing SQL: {}".format(sql))

        all_alarm = self.select(sql)

        return [AlarmEvent(x) for x in all_alarm] if all_alarm else []

    ###################################################
    # ALARM CONFIG
    ###################################################

    def select_alarm_config(self) -> AlarmConfig:
        config = self.select_config(AlarmConfig.CONFIG_NAME)

        return AlarmConfig(config) if config else None

    ###################################################
    # MONITORING CONFIG
    ###################################################

    def select_monitoring_config(self) -> MonitoringConfig:
        config = self.select_config(MonitoringConfig.CONFIG_NAME)

        return MonitoringConfig(config) if config else None

    ###################################################
    # SLEEP CONFIG
    ###################################################

    def select_awake_detection_config(self) -> AwakeDetectionConfig:
        config = self.select_config(AwakeDetectionConfig.CONFIG_NAME)

        return AwakeDetectionConfig(config) if config else None

    ###################################################
    # USER
    ###################################################

    def insert_user_data(self, data: dict) -> bool:
        '''
        return true if inserted successfully, else return false
        '''

        sql = '''
        insert into user 
        (first_name, last_name, username, salt, password) 
        values (?, ?, ?, ?, ?);'''

        try:
            self.__connect__()
            self.cur.execute(sql, (data["first_name"],
                                   data["last_name"],
                                   data["username"],
                                   data["salt"],
                                   data["password"])
                             )
            self.con.commit()

            return True
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

            return False

    def select_user_by_username(self, username: str) -> User:
        sql = '''
        select *
        from user
        where username = '{}';
        '''.format(username)

        print("Executing SQL: {}".format(sql))

        user = self.select(sql)

        return User(user[0]) if user else None

    ###################################################
    # BABY
    ###################################################

    def insert_baby_profile(self, data: dict) -> bool:
        sql = '''
        insert into baby_profile 
        (first_name, last_name, age, height, weight, image, user_id, devicename) values 
        (?, ?, ?, ?, ?, ?, ?, ?);
        '''

        try:
            self.__connect__()
            self.cur.execute(sql, (data["first_name"],
                                   data["last_name"],
                                   data["age"],
                                   data["height"],
                                   data["weight"],
                                   data["image"],
                                   data["user_id"],
                                   data["devicename"]
                                   )
                             )
            self.con.commit()

            return True
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

            return False

    def select_baby_profile_by_id_and_user_id(self, id: int, user_id: int) -> BabyProfile:
        sql = '''
        select *
        from baby_profile
        where id = {}
        and user_id = {};
        '''.format(id, user_id)

        print("Executing SQL: {}".format(sql))

        baby = self.select(sql)

        return BabyProfile(baby[0]) if baby else None

    def select_baby_profile_by_user_id(self, user_id: int) -> list[BabyProfile]:
        sql = '''
        select *
        from baby_profile
        where user_id = {};
        '''.format(user_id)

        print("Executing SQL: {}".format(sql))

        all_baby = self.select(sql)

        return [BabyProfile(x) for x in all_baby] if all_baby else []

    def update_baby_baby_profile_by_id(self, data: dict):
        sql = '''
        UPDATE baby_profile 
        SET first_name = ?, last_name = ?, age = ?, height = ?, weight = ?, image = ?, devicename = ?
        WHERE id = ?;
        '''

        try:
            self.__connect__()
            self.cur.execute(sql, (data["first_name"],
                                   data["last_name"],
                                   data["age"],
                                   data["height"],
                                   data["weight"],
                                   data["image"],
                                   data["devicename"],
                                   data["id"]
                                   )
                             )
            self.con.commit()

            return True
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

            return False
