import base64
import json


class User:
    def __init__(self, data) -> None:
        self.id = data[0]
        self.first_name = data[1]
        self.last_name = data[2]
        self.username = data[3]
        self.salt = data[4]
        self.password = data[5]

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "username": self.username,
            "salt": self.salt,
            "password": self.password
        }


class BabyProfile:
    def __init__(self, data) -> None:
        self.id = data[0]
        self.first_name = data[1]
        self.last_name = data[2]
        self.age = data[3]
        self.height = data[4]
        self.weight = data[5]
        self.image = data[6]
        self.user_id = data[7]
        self.devicename = data[8]

    def encode_image_b64(self):
        '''
        converts from binary -> base64 bytes -> base64 encoded string
        '''
        self.image = base64.b64encode(self.image).decode('utf-8')
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "age": self.age,
            "height": self.height,
            "weight": self.weight,
            "image": self.image,
            "user_id": self.user_id,
            "devicename": self.devicename
        }

###################################################
# SENSOR
###################################################


class SensorData:

    def __init__(self, data) -> None:
        self.id = data[0]
        self.devicename = data[1]
        self.pressure = data[2]
        self.gyro = data[3]
        self.leftdistance = data[4]
        self.rightdistance = data[5]
        self.temperature = data[6]
        self.image = data[7]  # this is stored as BLOB in DB
        self.timestamp = data[8]
        self.is_flipped = data[9]
        self.is_flipped_prob = data[10]
        self.is_eye_open = data[11]
        self.is_relayed = data[12]

    def encode_image_b64(self):
        '''
        converts from binary -> base64 bytes -> base64 encoded string
        '''
        self.image = base64.b64encode(self.image).decode('utf-8')
        return self

    def to_dict(self):
        return {
            "id": self.id,
            "devicename": self.devicename,
            "pressure": self.pressure,
            "gyro": self.gyro,
            "leftdistance": self.leftdistance,
            "rightdistance": self.rightdistance,
            "temperature": self.temperature,
            "image": self.image,
            "timestamp": str(self.timestamp),
            "is_flipped":  self.is_flipped,
            "is_flipped_prob": self.is_flipped_prob,
            "is_eye_open": self.is_eye_open,
            "is_relayed": self.is_relayed
        }

###################################################
# ALARM
###################################################


class AlarmEvent:

    def __init__(self, data) -> None:
        self.id = data[0]
        self.devicename = data[1]
        self.timestamp = data[2]
        self.interval_start = data[3]
        self.interval_end = data[4]
        self.sensor_data_count = data[5]
        self.flipped_count = data[6]
        self.ratio = data[7]
        self.threshold = data[8]

    def to_dict(self):
        return {
            "id": self.id,
            "devicename": self.devicename,
            "timestamp": self.timestamp,
            "interval_start": self.interval_start,
            "interval_end": self.interval_end,
            "sensor_data_count": self.sensor_data_count,
            "flipped_count": self.flipped_count,
            "ratio": self.ratio,
            "threshold": self.threshold
        }

###################################################
# CONFIG
###################################################


class Config:
    def __init__(self, data) -> None:
        self.id = data[0]
        self.name = data[1]
        self.config = data[2]


class AlarmConfig(Config):

    CONFIG_NAME = "alarm"

    def __init__(self, data) -> None:
        super().__init__(data)
        self.parsed_config = json.loads(self.config)
        self.monitoring_interval = self.parsed_config["monitoring_interval"]
        self.alarm_threshold = self.parsed_config["alarm_threshold"]
        self.toggle_fog_alarm = self.parsed_config["toggle_fog_alarm"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config,
            "monitoring_interval": self.monitoring_interval,
            "alarm_threshold": self.alarm_threshold,
            "toggle_fog_alarm": self.toggle_fog_alarm
        }


class MonitoringConfig(Config):

    CONFIG_NAME = "monitoring"

    def __init__(self, data) -> None:
        super().__init__(data)
        self.parsed_config = json.loads(self.config)
        self.monitoring_interval = self.parsed_config["monitoring_interval"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config,
            "monitoring_interval": self.monitoring_interval
        }


class AwakeDetectionConfig(Config):

    CONFIG_NAME = "awake_detection"

    def __init__(self, data) -> None:
        super().__init__(data)
        self.parsed_config = json.loads(self.config)
        self.awake_threshold = self.parsed_config["awake_threshold"]

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "config": self.config,
            "awake_threshold": self.awake_threshold
        }
