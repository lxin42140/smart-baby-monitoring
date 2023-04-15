import sqlite3
from .models import SensorData
import base64


class DBHelper:

    def __init__(self, db_name) -> None:
        self.db_name = db_name
        pass

    # establish connection
    def __connect__(self):
        try:
            self.con = sqlite3.connect(self.db_name)
            self.cur = self.con.cursor()
        except Exception as e:
            print("Exception occurred:{}".format(e))

    # disconnect db
    def __disconnect__(self):
        self.con.close()
        self.cur = None

    # insert data
    def execute(self, sql) -> None:
        try:
            self.__connect__()
            self.cur.execute(sql)
            self.con.commit()
        except Exception as e:
            print("Exception occurred:{}".format(e))
        finally:
            self.__disconnect__()

    # read data
    def select(self, sql) -> list:
        try:
            self.__connect__()
            self.cur.execute(sql)
            result = self.cur.fetchall()
            return result
        except Exception as e:
            print("Exception occurred:{}".format(e))
        finally:
            self.__disconnect__()

    def select_sensor_data_later_than_id(self, id: int):
        filtered_data = self.select(
            'select * from sensor where id > {} order by id desc;'.format(id))
        if filtered_data is not None:
            return [SensorData(x) for x in filtered_data]
        
    def convertToBinaryData(filePath):
        with open(filePath, 'rb') as file:
            file = file.read()

        return sqlite3.Binary(file)

    ###################################################
    ###             SELECT                       ######
    ###################################################

    def select_all_sensor_data(self) -> 'list[SensorData]':
        all_sensor_data = self.select('select * from sensor order by id desc;')
        return [SensorData(x) for x in all_sensor_data] if all_sensor_data is not None else []
    
    def select_last_record_id(self):
        all_sensor_data = self.select('select id from sensor order by id desc;')
        if all_sensor_data is not None and len(all_sensor_data) > 0:
            return all_sensor_data[0]
        else:
            return -1

    def select_unrelayed_sensor_data(self) -> 'list[SensorData]':
        unrelayed_data = self.select(
            'select * from sensor where is_relayed = 0 order by id desc;')

        return [SensorData(x) for x in unrelayed_data]
    def select_sensor_data_fog(self):
        sensor_data = self.select("Select devicename, \
                                    AVG(pressure) AS averagepressure, \
                                    AVG(gyro) As averagegyro, \
                                    AVG(leftdistance) as averageld, \
                                    AVG(rightdistance) as averagerd, \
                                    AVG(temperature) as averagetemp \
                                    FROM sensor \
                                    GROUP BY devicename ORDER BY devicename ASC")
        return sensor_data
    
    def select_image_data_fog(self):
        image_data = self.select("Select devicename, image, timestamp from sensor")
        fogDict = {}
        for data in image_data:
            devicename = data[0]
            image = base64.b64encode(data[1]).decode('utf-8')
            timestamp = data[2]
            if devicename not in fogDict:
                fogDict[devicename] = [{"timestamp": timestamp, "image": image}]
            else:
                currentFogArray = fogDict[devicename]
                currentFogArray.append({"timestamp": timestamp, "image": image})
                fogDict[devicename] = currentFogArray
        return fogDict

    ###################################################
    ###             INSERT                       ######
    ###################################################

    def insert_sensor_data(self, data: dict) -> None:
        sql = "insert into sensor (devicename, pressure, gyro, leftdistance, rightdistance, temperature, image, timestamp, is_flipped, is_flipped_prob, is_eye_open, is_relayed) values (?, ?, ?, ?, ?, ?, ?, datetime('now', 'localtime'), ?, ?, ?, ?)"

        try:
            self.__connect__()
            self.cur.execute(sql, (data["devicename"],
                                   data["pressure"],
                                   data["gyro"],
                                   data["leftdistance"],
                                   data["rightdistance"],
                                   data["temperature"],
                                   data["image"],
                                   data.get("is_flipped", -1),
                                   data.get("is_flipped_prob", -1),
                                   data.get("is_eye_open", -1),
                                   data.get("is_relayed", 0))
                             )
            self.con.commit()
        except Exception as e:
            print("ERROR: {}".format(e))
            self.__disconnect__()

    ###################################################
    ###             UPDATE                       ######
    ###################################################

    def update_relayed_sensor_data(self, ids: 'list[int]') -> None:
        sql = "update sensor set is_relayed = 1 where id in ({});".format(
            ','.join([str(id) for id in ids]))

        self.execute(sql)
