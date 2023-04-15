import threading
import time
import random
import requests
import json
from flask import Flask, render_template, make_response, abort
from db.sql_db_helper import DBHelper
from hub import Hub

############################ START OF DB ############################

dbHelper = DBHelper(db_name='fog.db')

############################ START OF HUB ############################
# cloud config
HEADERS = {'content-type': 'application/json'}
# TODO: add corresponding fog ip
CLOUD_BASE_URIS = [#"http://192.168.1.40:23336",\
                   #"http://192.168.1.61:23336",\
                   #"http://172.25.106.101:23336"\
                   "http://192.168.137.26:23336"]  # li xin macBook air, benny Laptop
CLOUD_SENSOR_DATE_URI = "/data/sensor"
HUB_NAME="hub1"

# hub config
hub = Hub(hub_name=HUB_NAME, connect_radio=True)


def run_monitor_baby():
    '''
    Every 10 seconds, poll data from sensor and relay data to cloud
    '''

    while True:
        if not hub.alarm_activated:
            print("********Getting readings...********")

            hub.monitor_baby_readings()

            print("********Relaying sensor data...********")
            # get unrelayed data from DB
            data_to_relay = dbHelper.select_unrelayed_sensor_data()

            if len(data_to_relay) > 0:
                # encode image from binary to base64, then convert to a dict
                data_to_relay = [data.encode_image_b64().to_dict()
                                 for data in data_to_relay]

                print(data_to_relay)
                
                hasConnectedAndSent = False

                # send data to cloud
                for ip in CLOUD_BASE_URIS:
                    try:
                        requests.post(url=ip + CLOUD_SENSOR_DATE_URI,
                                    data=json.dumps(data_to_relay),
                                    headers=HEADERS)
                        hasConnectedAndSent = True
                    except Exception:
                        print("Error connecting to {}".format(ip))
                        pass

                # update state from unrelayed to relayed
                if hasConnectedAndSent:
                    dbHelper.update_relayed_sensor_data(
                        [x["id"] for x in data_to_relay])

            else:
                print("No data to relay!")

        time.sleep(10)


############################ START OF FLASK ############################

host_name = "0.0.0.0"
port = 23336
app = Flask(__name__)


@app.route("/data/sensor-data", methods=['GET'])
def index():
    return render_template('sensor_data.html',
                           title='Fog Processor {}'.format(hub.hub_name),
                           readings=dbHelper.select_sensor_data_fog(), fogImages=dbHelper.select_image_data_fog())


@app.route("/command/alarm/<state>", methods=['GET'])
def toggle_alarm(state: str):

    if "on" in state.lower():
        print("alarm toggled")
        hub.activate_alarm()

        return make_response("Alarm activated!", 200)
    elif "off" in state.lower():
        hub.deactivate_alarm()

        return make_response("Alarm deactivated!", 200)
    else:
        return abort(
            404,
            "Wrong request parameter: {} - only 'on' and 'off' are accepted! ".
            format(state))

############################ START OF MAIN ############################


if __name__ == "__main__":
    threading.Thread(target=lambda: app.run(
        host=host_name, port=port, debug=False, use_reloader=False)).start()

    threading.Thread(target=run_monitor_baby).start()
