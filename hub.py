import time
import sqlite3
import serial
import math
import json
# GPIO imports
import RPi.GPIO as GPIO
from node.Adafruit_BME280 import *
from node import camera
# DB import
from db.sql_db_helper import DBHelper as SqlHelper
IMAGE_FOLDER_ROOT_DIR = './images/sensor/'


class Hub:

    def __init__(self, hub_name, connect_radio) -> None:
        print("********Initiating hub:{}...********".format(hub_name))
        try:
            self.hub_name = hub_name

            # GPIO
            GPIO.setmode(GPIO.BOARD)

            # LED
            self.ledRedPin = 40
            self.__toggle_fog_led(on=True)
            self.__toggle_fog_led(on=False)

            # connect to BME
            self.bme = BME280(t_mode=BME280_OSAMPLE_8, 
                              p_mode=BME280_OSAMPLE_8,
                              h_mode=BME280_OSAMPLE_8)

            # connect to radio
            self.connected_radio = connect_radio

            if connect_radio:
                self.connected_node_devices = []
                self.ser = serial.Serial(port='/dev/ttyACM0',
                                         baudrate=115200,
                                         timeout=1)

                # FIXME: change here. tentatively still 2
                while len(self.connected_node_devices) != 2:
                    print("resetting radio...")
                    self.radio_reset()
                    time.sleep(5)
                    print("handshaking...")
                    self.radio_handshake()
                    time.sleep(5)

            # connect to db
            self.sql_db = SqlHelper(db_name='fog.db')

            # alarm
            self.alarm_activated = False

        except Exception as err:
            raise Exception("********INIT FAILED: {}********".format(err))

    ############################ START OF FOG COMMANDS ############################
    def monitor_baby_readings(self):
        print("Getting reading from node devices...")

        combined_sensor_data = {}

        if self.connected_radio:
            combined_sensor_data = self.__get_data_from_node('sensor=all')
        

        temp = int(self.bme.read_temperature())
        combined_sensor_data['temperature'] = '{0:0.1f}'.format(temp)  # 1 d.p

        combined_sensor_data['devicename'] = self.hub_name

        # get data from camera, Blob format (blob is just a large binary object)
        
        combined_sensor_data['image'] = camera.captureImage(IMAGE_FOLDER_ROOT_DIR)
        
        # mock right distance
        combined_sensor_data["rightdistance"] = 50
        
        
        print("Combined_sensor_data sensor reading: {}".format(
            combined_sensor_data))

        
        self.sql_db.insert_sensor_data(combined_sensor_data)
        # for testing
        # test_result = self.sql_db.select("SELECT name FROM sqlite_master WHERE type='table';")
        # print(test_result)


        return combined_sensor_data

    ############################ START OF NODE COMMANDS ############################

    def radio_reset(self):
        self.__send_command('reset')

    def radio_handshake(self):
        print("Connecting fog to micro:bit devices...")
        self.__send_command('handshake')

        strMicrobitDevices = None

        while strMicrobitDevices == None or len(strMicrobitDevices) <= 0:
            strMicrobitDevices = self.__wait_response()
            time.sleep(0.1)

        print(strMicrobitDevices)

        # strMicrobitDevices format is enrol=deviceNameA,deviceNameB...
        strMicrobitDevices = strMicrobitDevices.split('=')

        # get list of devices
        if len(strMicrobitDevices[1]) > 0:
            # get individual device name
            self.connected_node_devices = strMicrobitDevices[1].split(',')

            if len(self.connected_node_devices) > 0:
                for mb in self.connected_node_devices:
                    print('Connected to micro:bit device {}...'.format(mb))

    def activate_alarm(self):
        self.alarm_activated = True
        self.__toggle_fog_led(True)
        self.__send_command("cmd:alarm=on")

        # TODO: add command to on node alarm

    def deactivate_alarm(self):
        self.alarm_activated = False
        self.__toggle_fog_led(False)
        self.__send_command("cmd:alarm=off")
        # TODO: add command to off node alarm

    def __get_data_from_node(self, commandToTx: str) -> list:
        print("Getting {}...".format(commandToTx))

        self.__send_command('cmd:' + commandToTx)

        strSensorValues = None

        while strSensorValues == None or len(strSensorValues) <= 0:
            strSensorValues = self.__wait_response()
            time.sleep(0.1)

        sensorValuesDict = {}

        listSensorValues = strSensorValues.split(',')

        for sensorValue in listSensorValues:
            keyValue = sensorValue.split("=")
            key = keyValue[0]
            value = keyValue[1]
            sensorValuesDict[key] = value

        print(listSensorValues)

        # did not get data from all node devices, retry
        if len(listSensorValues) < len(self.connected_node_devices):
            print("did not receive feedback from all nodes, retrying...")

            listSensorValues = self.__get_data_from_node(commandToTx)

        # return listSensorValues
        return sensorValuesDict

    def __toggle_fog_led(self, on):
        GPIO.setup(self.ledRedPin, GPIO.OUT)
        GPIO.output(self.ledRedPin, not on)
       
    def __send_command(self, command):
        command = command + '\n'
        self.ser.write(str.encode(command))

    def __wait_response(self) -> str:
        response = self.ser.readline()
        response = response.decode('utf-8').strip()
        return response

    def __del__(self):
        GPIO.cleanup()
