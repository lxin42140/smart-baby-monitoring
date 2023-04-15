import threading
import time
import requests
import json
import base64
import math
from datetime import datetime
import datetime as dt
import os
import json
import pandas as pd
import hashlib
import time
from db.models import *
from PIL import Image
from flask import Flask, make_response, abort, request, jsonify
from db.cloud_db_helper import CloudDBHelper
from ml.baby_posture_detection import BabyPostureDetection
from flask_socketio import SocketIO
from sklearn.preprocessing import MinMaxScaler
from functools import wraps
from flask_cors import CORS


############################ CONSTANTS ############################

HEADERS = {'content-type': 'application/json'}

# TODO: add IP address and device name
FOG_NAME_IP_MAPPING = {
    "xin_fog_1": ["http://192.168.1.132:23336"],
    "xin_fog_2": ["http://192.168.1.127:23336"],
    "hub1": ["http://192.168.137.219:23336"],
    "ky_fog_1": ["http://172.20.10.6:23336"],
    "all": ["http://192.168.1.132:23336", "http://192.168.1.127:23336"]
}
FOG_COMMAND_MAPPING = {
    "alarm": "/command/alarm/"
}
FOG_COMMAND_STATE_MAPPING = {
    "on": "on",
    "off": "off"
}
CONFIG = {
    AlarmConfig.CONFIG_NAME: {
        "name": AlarmConfig.CONFIG_NAME,
        "config": {
            "monitoring_interval": 1,  # mins
            "alarm_threshold": 70,  # out of 100
            "toggle_fog_alarm": 1  # 1 for true 0 for false
        }
    },
    MonitoringConfig.CONFIG_NAME: {
        "name": MonitoringConfig.CONFIG_NAME,
        "config": {
            "monitoring_interval": 30,  # seconds
        }
    },
    AwakeDetectionConfig.CONFIG_NAME: {
        "name": AwakeDetectionConfig.CONFIG_NAME,
        "config": {
            "awake_threshold": 0.5,  # between 0 and 1, higher threshold, lower sensitivity
        }
    }
}
CACHE = {
    "sleep": {}
}
session = {}
############################ Setup ############################

host_name = "0.0.0.0"
port = 23336
app = Flask(__name__)
CORS(app)
app.secret_key = os.urandom(32)
socketio = SocketIO(app, cors_allowed_origins="*")

model = BabyPostureDetection()
dbHelper = CloudDBHelper(db_name='cloud.db')

############################ Config ############################

# init alarm config
if dbHelper.select_alarm_config() is None:
    dbHelper.insert_config(CONFIG[AlarmConfig.CONFIG_NAME])

# init monitoring config
if dbHelper.select_monitoring_config() is None:
    dbHelper.insert_config(CONFIG[MonitoringConfig.CONFIG_NAME])

# init sleep detection config
if dbHelper.select_awake_detection_config() is None:
    dbHelper.insert_config(CONFIG[AwakeDetectionConfig.CONFIG_NAME])

############################ Monitoring ############################

alarm_activated = False


def monitor_baby_posture():
    global alarm_activated

    print(alarm_activated)

    while True:
        if not alarm_activated:
            print("==================================================")
            print("====================MONITORING====================")
            print("==================================================")

            start_time = time.time()
            # retrieve latest config
            alarm_config = dbHelper.select_alarm_config()

            for fog in FOG_NAME_IP_MAPPING.keys():
                if fog == "all":
                    continue

                print("=========={}================".format(fog))

                # get the current time
                current_time = datetime.now()

                # start of interval
                start_time = current_time - \
                    dt.timedelta(minutes=alarm_config.monitoring_interval)

                start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")

                # get total data count in interval
                num_data = dbHelper.select_count_by_fog_and_time(
                    fog, start_time)

                if num_data == 0:
                    print("No data from fog {}", format(fog))

                    continue

                # get flipped count in interval
                num_fipped = dbHelper.select_count_flipped_by_fog_and_time(
                    fog, start_time)

                # determine ratio
                flipped_ratio = math.floor((num_fipped / num_data) * 100)

                print("Flipped score: {}".format(flipped_ratio))
                print("Threshold: {}".format(alarm_config.alarm_threshold))

                if flipped_ratio >= alarm_config.alarm_threshold:
                    new_alert_data = {
                        "devicename": fog,
                        "interval_start": start_time,
                        "interval_end": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                        "sensor_data_count": num_data,
                        "flipped_count": num_fipped,
                        "ratio": flipped_ratio,
                        "threshold": alarm_config.alarm_threshold
                    }

                    # insert alarm event in db
                    dbHelper.insert_alarm_event(new_alert_data)

                    # toggle alarm to corresponding fog
                    if alarm_config.toggle_fog_alarm == 1:
                        for ip in FOG_NAME_IP_MAPPING[fog]:
                            address = ip + \
                                FOG_COMMAND_MAPPING["alarm"] + \
                                FOG_COMMAND_STATE_MAPPING["on"]
                            print("Toggling alarm at - {}".format(address))
                            requests.get(address)

                    # push alert to frontend over ws
                    socketio.emit('flipped_alarm', json.dumps(new_alert_data))

                    alarm_activated = True

            sleep_interval = dbHelper.select_monitoring_config().monitoring_interval

            print("==================================================")

        time.sleep(sleep_interval)

############################ FLASK ############################


def is_valid_date(date_string):
    try:
        datetime.strptime(date_string, '%Y-%m-%d %H:%M:%S')
        return True
    except ValueError:
        return False


def generate_cache_key(name, start, end) -> str:
    return name + "-" + start + "-" + end


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'is_logged_in' not in session:
            return abort(404, "Please login first!")
        return f(*args, **kwargs)
    return decorated_function


###################################################
# WS
###################################################

@socketio.on('connect')
def connect():
    if 'is_logged_in' in session.keys():
        pass
        # socketio.start_background_task(send_data_periodically)


@socketio.on('disconnect')
def disconnect():

    socketio.stop()

###################################################
# SENSOR
###################################################


@app.route("/data/sensor", methods=['POST'])
# @login_required
def post_sensor_data():
    # decode from json
    payload = json.dumps(request.get_json())
    payload_arr: list[dict] = json.loads(payload)

    for data in payload_arr:
        # check if fog server is legit
        if data["devicename"] not in FOG_NAME_IP_MAPPING.keys():
            return abort(
                404,
                "Fog {} not supported - only accept: {}".
                format(data["devicename"], list(FOG_NAME_IP_MAPPING.keys())))

        # decode each base64 image to get original binary
        data['image'] = base64.b64decode(data['image'])

        # save raw binary
        result_file = os.path.abspath('images/sensor/{}'.format(data['id']))
        with open(result_file, 'wb') as f:
            f.write(data['image'])

        # convert binary to image
        img = Image.open(result_file)
        img.save(result_file + '.jpeg')

        # delete binary file
        os.remove(result_file)

        # predict if is flipped
        flipped_outcome, is_flipped_prob = model.predict_flip(
            ["{}.jpeg".format(data['id']), data['pressure'], data['gyro'], data['leftdistance'], data['rightdistance']])

        # save prediction outcome
        data['is_flipped'] = flipped_outcome
        data['is_flipped_prob'] = is_flipped_prob

        # determine if eye is open
        is_eye_open = model.detect_eye_open_close_in_image(
            "{}.jpeg".format(data['id']))

        data['is_eye_open'] = 1 if is_eye_open else 0

        print("Inserting data: {}".format(data))

        dbHelper.insert_sensor_data(data)

    return make_response("{} sensor data added!".format(len(payload_arr)), 200)


@app.route("/data/sensor", methods=['GET'])
@login_required
def get_sensor_data():
    all_sensor_data = dbHelper.select_all_sensor_data()
    all_sensor_data = [data.encode_image_b64().to_dict()
                       for data in all_sensor_data]

    return jsonify(all_sensor_data)


@app.route("/data/sensor/<fog_name>", methods=['GET'])
@login_required
def get_sensor_data_for_fog(fog_name):

    all_sensor_data = []

    # check query parameters
    args = request.args.to_dict()

    if "start_time" in args.keys() and "end_time" in args.keys():  # filter for fog
        start_time = args["start_time"]
        end_time = args["end_time"]

        if not is_valid_date(start_time) or not is_valid_date(end_time):
            return abort(404, "Invalid datetime format - required 'YYYY MM DD HH:MM:SS'")

        all_sensor_data = dbHelper.select_sensor_data_between_interval_for_fog(
            fog_name, start_time, end_time)
    else:  # get all for fog
        all_sensor_data = dbHelper.select_sensor_data_for_fog(fog_name)

    all_sensor_data = [data.encode_image_b64().to_dict()
                       for data in all_sensor_data]

    return jsonify(all_sensor_data)

###################################################
# ALARM EVENT
###################################################


@app.route("/data/alarm", methods=['GET'])
@login_required
def get_alarm_data():
    all_alarm_data = dbHelper.select_all_alarm_event()
    all_alarm_data = [data.to_dict() for data in all_alarm_data]

    return jsonify(all_alarm_data)


@app.route("/data/alarm/<fog_name>", methods=['GET'])
@login_required
def get_alarm_data_for_fog(fog_name):

    all_alarm_data = []

    # check query parameters
    args = request.args.to_dict()

    if "start_time" in args.keys() and "end_time" in args.keys():  # filter for fog
        start_time = args["start_time"]
        end_time = args["end_time"]

        if not is_valid_date(start_time) or not is_valid_date(end_time):
            return abort(404, "Invalid datetime format - required 'YYYY MM DD HH:MM:SS'")

        all_alarm_data = dbHelper.select_alarm_between_interval_for_fog(
            fog_name, start_time, end_time)
    else:  # get all for fog
        all_alarm_data = dbHelper.select_all_alarm_for_fog(fog_name)

    all_alarm_data = [data.to_dict() for data in all_alarm_data]

    return jsonify(all_alarm_data)

###################################################
# CONFIG
###################################################


@app.route("/data/config/default", methods=['GET'])
@login_required
def get_default_config():
    return jsonify(CONFIG)


@app.route("/data/config/<config_name>", methods=['GET'])
@login_required
def get_config(config_name: str):
    if config_name is not None and config_name.lower() == AlarmConfig.CONFIG_NAME:  # alarm config
        alarm_config = dbHelper.select_alarm_config()
        return jsonify(alarm_config.to_dict())
    elif config_name is not None and config_name.lower() == MonitoringConfig.CONFIG_NAME:  # monitoring config
        monitor_config = dbHelper.select_monitoring_config()
        return jsonify(monitor_config.to_dict())
    elif config_name is not None and config_name.lower() == AwakeDetectionConfig.CONFIG_NAME:  # awake detection config
        sleep_config = dbHelper.select_awake_detection_config()  # server config
        return jsonify(sleep_config.to_dict())
    elif config_name is not None and config_name.lower() == "server":
        return jsonify({
            "fog_name": list(FOG_NAME_IP_MAPPING.keys()),
            "fog_command": list(FOG_COMMAND_MAPPING.keys()),
            "fog_state": list(FOG_COMMAND_STATE_MAPPING.keys())
        })
    else:
        return abort(404, "No matching config!")


@app.route("/data/config/<config_name>", methods=['POST'])
@login_required
def update_config(config_name):
    payload: dict = json.loads(request.get_data().decode())

    # check param
    if payload["name"] is None or payload["config"] is None:
        return abort(
            404,
            "Incomplete config data - missing 'name' or 'config'")

    # check config
    is_valid = False
    config: dict = payload["config"]

    if config_name == AlarmConfig.CONFIG_NAME and \
            payload["name"] == AlarmConfig.CONFIG_NAME and \
            "monitoring_interval" in config.keys() and \
            "alarm_threshold" in config.keys() and \
            "toggle_fog_alarm" in config.keys():

        is_valid = True
    elif config_name == MonitoringConfig.CONFIG_NAME and \
            payload["name"] == MonitoringConfig.CONFIG_NAME and \
            "monitoring_interval" in config.keys():

        is_valid = True
    elif config_name == AwakeDetectionConfig.CONFIG_NAME and \
            payload["name"] == AwakeDetectionConfig.CONFIG_NAME and \
            "awake_threshold" in config.keys():

        is_valid = True

    # update config
    if is_valid:
        dbHelper.update_config(payload)
        return make_response("{} config updated!".format(config_name), 200)
    else:
        return abort(
            404,
            "Invalid config!")

###################################################
# SLEEP
###################################################


@app.route("/data/sleep/<fog_name>", methods=['GET'])
@login_required
def get_sleep_data(fog_name: str):
    existing_fogs: set = list(FOG_NAME_IP_MAPPING.keys())
    existing_fogs.remove("all")

    # check fog
    if fog_name.lower() not in existing_fogs:
        return abort(
            404,
            "Fog {} not valid - only accept: {}".
            format(fog_name, list(existing_fogs)))

    # check query parameters
    args = request.args.to_dict()

    if "start_time" not in args.keys() or \
        "end_time" not in args.keys() or \
            "reset" not in args.keys():
        return abort(404, "start_time and/or end_time not provided!")

    start_time = args["start_time"]
    end_time = args["end_time"]
    reset = args["reset"]  # forced re-compute of sleep data

    if not is_valid_date(start_time) or not is_valid_date(end_time):
        return abort(404, "Invalid datetime format - required 'YYYY MM DD HH:MM:SS'")

    ######################
    # cache
    ######################

    cache_key = generate_cache_key(fog_name, start_time, end_time)

    if cache_key in CACHE["sleep"].keys() and reset == 0:
        return jsonify(CACHE["sleep"][cache_key])

    ######################
    # compute sleep data if data has not been computed before
    ######################

    sleep_detection_config = dbHelper.select_awake_detection_config()

    # retrieve sensor data between the time range for the required fog
    sensor_data = dbHelper.select_sensor_data_between_interval_for_fog(
        fog_name, start_time, end_time)

    if (sensor_data is None or len(sensor_data) == 0):
        return make_response("No sensor data between range for fog: {} - {} for fog {}".format(start_time, end_time, fog_name))

    # convert sensor data to a pandas data frame for analysis
    data = {
        'gyro': [int(x.gyro) for x in sensor_data],
        'leftdistance': [float(x.leftdistance) for x in sensor_data],
        'rightdistance': [float(x.rightdistance) for x in sensor_data],
        'is_eye_open': [int(x.is_eye_open) for x in sensor_data],
        'timestamp': [datetime.strptime(x.timestamp, "%Y-%m-%d %H:%M:%S") for x in sensor_data],
        'is_awake': [0 for i in range(len(sensor_data))]
    }

    # Create DataFrame
    df = pd.DataFrame(data, columns=[
                      'gyro', 'leftdistance', 'rightdistance', 'is_eye_open', 'timestamp', 'is_awake'])

    # Aggregate the dataframe in 5-minute blocks based on the timestamp column
    df_agg = df.set_index('timestamp').resample('5T').agg({
        'gyro': 'sum',
        'leftdistance': 'sum',
        'rightdistance': 'sum',
        'is_eye_open': 'max',
        'is_awake': 'max'
    })

    # Set 'is_awake' to 1 for each 5-minute block where 'is_eye_open' is 1
    df_agg.loc[df_agg['is_eye_open'] == 1, 'is_awake'] = 1

    # Calculate the difference between the value of rows of 'gyro', 'leftdistance', 'rightdistance' in the 5 min block
    df_agg['diff_gyro'] = df_agg['gyro'].diff().fillna(0)
    df_agg['diff_leftdistance'] = df_agg['leftdistance'].diff().fillna(0)
    df_agg['diff_rightdistance'] = df_agg['rightdistance'].diff().fillna(0)

    # Calculate the absolute sum of differences for each 5-minute block
    df_agg['abs_diff'] = abs(df_agg['diff_gyro']) + abs(
        df_agg['diff_leftdistance']) + abs(df_agg['diff_rightdistance'])

    # scale the diff
    scaler = MinMaxScaler()
    df_agg['abs_diff_scaled'] = df_agg['abs_diff'].astype(float)
    df_agg['abs_diff_scaled'] = scaler.fit_transform(df_agg[['abs_diff']])

    # Set 'is_awake' to True for each 5-minute block where the scaled absolute sum of differences is greater than threshold
    df_agg.loc[df_agg['abs_diff_scaled'] >
               sleep_detection_config.awake_threshold, 'is_awake'] = 1

    # Print the head of the aggregated dataframe
    print(df_agg.head())

    # extract out processed sleep data and combine them
    timestamp = df_agg.index.tolist()
    timestamp = [x.strftime('%Y-%m-%d %H:%M:%S') for x in timestamp]
    is_awake = df_agg['is_awake'].tolist()
    processed_data = []

    for i in range(len(timestamp)):
        processed_data.append({
            'timestamp': timestamp[i],
            'is_awake': is_awake[i]
        })

    # store result in cache
    CACHE["sleep"][cache_key] = processed_data

    return jsonify(processed_data)

###################################################
# COMMAND
###################################################


@app.route("/command/<fog_name>/<command>/<state>", methods=['GET'])
@login_required
def send_command(fog_name: str, command: str, state: str):
    # check fog
    if fog_name not in FOG_NAME_IP_MAPPING.keys():
        return abort(
            404,
            "Fog {} not supported - only accept: {}".
            format(fog_name, list(FOG_NAME_IP_MAPPING.keys())))

    # check command
    if command not in FOG_COMMAND_MAPPING.keys():
        return abort(
            404,
            "Command {} not supported - only accept: {}".
            format(command, list(FOG_COMMAND_MAPPING.keys())))

    # check state
    if state not in FOG_COMMAND_STATE_MAPPING.keys():
        return abort(
            404,
            "State {} not supported - only accept: {}".
            format(state, list(FOG_COMMAND_STATE_MAPPING.keys())))

    # toggle alarm_activated to control whether monitoring should be run
    global alarm_activated
    if command.lower() == "alarm":
        if state.lower() == "off":
            alarm_activated = False
        elif state.lower() == "on":
            alarm_activated = True

    # send command to corresponding fogs
    for base_uri in FOG_NAME_IP_MAPPING[fog_name]:
        address = base_uri + \
            FOG_COMMAND_MAPPING[command] + FOG_COMMAND_STATE_MAPPING[state]

        print("Toggling command at: {}".format(address))

        requests.get(address, headers=HEADERS)

    return make_response(
        "Command sent successfully!", 200)

###################################################
# LOGIN & AUTHENTICATION
###################################################


@app.route("/user/register", methods=['POST'])
def register_user():
    # get payload
    payload: dict = json.loads(request.get_data().decode())

    # check param
    if payload["first_name"] is None or \
            payload["last_name"] is None or \
            payload["username"] is None or \
            payload["password"] is None:
        return abort(
            404,
            "Incomplete user data!")

    # hash the password using the salt
    salt = os.urandom(32)
    payload["salt"] = salt

    hashed_password = hashlib.pbkdf2_hmac(
        'sha256', payload["password"].encode('utf-8'), salt, 100000)
    payload["password"] = hashed_password

    # save to DB
    if dbHelper.insert_user_data(payload):
        return make_response("Account created, please login", 200)
    else:
        return abort(404, "Create user failed, please try again with different username!")


@app.route("/user/login", methods=['POST'])
def login_user():
    # get payload
    payload: dict = json.loads(request.get_data().decode())

    # check param
    if payload["username"] is None or \
            payload["password"] is None:
        return abort(
            404,
            "Incomplete login data!")

    # get user
    user = dbHelper.select_user_by_username(payload["username"])
    if user is None:
        return abort(404, "user data does not exist in DB!")

    # generate hash
    hashed_pw = hashlib.pbkdf2_hmac(
        'sha256', payload["password"].encode('utf-8'), user.salt, 100000)

    # check password
    if hashed_pw != user.password:
        return abort(404, "Wrong password!")
    else:
        session["username"] = payload["username"]
        session["is_logged_in"] = True
        session["user_id"] = user.id

        return make_response("Logged in successfully!", 200)


@app.route("/user/logout", methods=['GET'])
@login_required
def logout_user():

    del session["username"]
    del session['is_logged_in']

    return make_response("User logged out successfully!", 200)


@app.route("/user/profile", methods=['GET'])
@login_required
def get_user_profile():
    user = dbHelper.select_user_by_username(session["username"]).to_dict()

    del user["password"]
    del user["salt"]

    return jsonify(user)

###################################################
# Baby profile
###################################################


@app.route("/baby/new", methods=['POST'])
@login_required
def add_baby_profile():
    # get payload
    data: dict = json.loads(request.get_data().decode())

    # decode image
    data['image'] = base64.b64decode(data['image'])

    # add user id
    data["user_id"] = session["user_id"]

    # check device name
    if not data["devicename"] or data["devicename"] not in FOG_NAME_IP_MAPPING.keys():
        abort(
            404, "Create baby profile failed - invalid fog name {}!".format(data["devicename"]))

    # save DB
    if dbHelper.insert_baby_profile(data):
        return make_response("Baby profile added successfully!", 200)
    else:
        abort(404, "Create baby profile failed - please check parameters!")


@app.route("/baby/<id>", methods=['GET'])
@login_required
def get_baby_profile(id: int):

    baby = dbHelper.select_baby_profile_by_id_and_user_id(
        id, session["user_id"])

    if baby:
        return jsonify(baby.encode_image_b64().to_dict())
    else:
        return abort(404, "Baby profile #{} not found!".format(id))


@app.route("/baby/all", methods=['GET'])
@login_required
def get_all_baby_profile():

    babies = dbHelper.select_baby_profile_by_user_id(session["user_id"])
    babies = [data.encode_image_b64().to_dict()
              for data in babies]

    return jsonify(babies)


@app.route("/baby/<id>", methods=['POST'])
def update_baby_profile(id: int):
    baby: BabyProfile = dbHelper.select_baby_profile_by_id_and_user_id(
        id, session["user_id"])

    if not baby:
        return abort(404, "Baby profile #{} not found!".format(id))

    data: dict = json.loads(request.get_data().decode())

    data["id"] = id

    # populate data with old data if not present
    if "image" not in data.keys():
        data["image"] = baby.image
    else:
        data['image'] = base64.b64decode(data['image'])

    if "first_name" not in data.keys():
        data["first_name"] = baby.first_name

    if "last_name" not in data.keys():
        data["last_name"] = baby.last_name

    if "age" not in data.keys():
        data["age"] = baby.age

    if "height" not in data.keys():
        data["height"] = baby.height

    if "weight" not in data.keys():
        data["weight"] = baby.weight

    if "devicename" not in data.keys():
        data["devicename"] = baby.devicename

    # check device name
    if not data["devicename"] or data["devicename"] not in FOG_NAME_IP_MAPPING.keys():
        abort(
            404, "Create baby profile failed - invalid fog name {}!".format(data["devicename"]))

    if dbHelper.update_baby_baby_profile_by_id(data):
        return make_response("Baby profile #{} updated successfully!".format(id))
    else:
        abort(404, "Update baby profile #{} failed!".format(id))


############################ MAIN ############################
if __name__ == "__main__":

    ############################ Threads ############################

    threading.Thread(target=lambda: socketio.run(
        app, host=host_name, port=port, debug=False, use_reloader=False)).start()

    threading.Thread(target=monitor_baby_posture).start()
