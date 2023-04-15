from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from faker_data_spoofer import device_names, generate_fake_data
from flask_socketio import SocketIO, emit
import os
from datetime import datetime
from faker import Faker
from itertools import cycle
import requests
from datetime import datetime,timedelta

app = Flask(__name__)
CORS(app)
# SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sensor_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
fake = Faker()
device_names = cycle(['Device1', 'Device2', 'Device3', 'Device4', 'Device5'])


class SensorData(db.Model):
    __tablename__ = 'sensor_data'

    id = db.Column(db.Integer, primary_key=True)
    devicename = db.Column(db.String(100))
    pressure = db.Column(db.Integer)
    gyro = db.Column(db.Integer)
    leftdistance = db.Column(db.Integer)
    rightdistance = db.Column(db.Integer)
    temperature = db.Column(db.Integer)
    image = db.Column(db.String(36))
    is_flipped = db.Column(db.Integer)
    is_flipped_prob = db.Column(db.Float)
    is_eye_open = db.Column(db.Integer)
    is_relayed = db.Column(db.Integer)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


class BabyData(db.Model):
    __tablename__ = 'baby_profile'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    height = db.Column(db.Float, nullable=False)
    weight = db.Column(db.Float, nullable=False)
    image = db.Column(db.LargeBinary)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    devicename = db.Column(db.String, nullable=False)

    user = db.relationship(
        'User', backref=db.backref('baby_profile', lazy=True))

    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'age': self.age,
            'height': self.height,
            'weight': self.weight,
            # You might want to convert the image to a different format before sending it as JSON
            'image': self.image,
            'user_id': self.user_id,
            'devicename': self.devicename
        }


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    salt = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def __repr__(self):
        return f"<User(id={self.id}, username={self.username}, first_name={self.first_name}, last_name={self.last_name})>"


@app.route('/data/sensor', methods=['POST'])
def store_sensor_data():
    data = request.get_json()
    sensor_data = SensorData(**data)
    db.session.add(sensor_data)
    db.session.commit()
    # Emit event every time it is posted.
    socketio.emit('new_data', data)
    return jsonify({"result": "success"}), 201


@app.route('/data/sensor', methods=['GET'])
def get_sensor_data():
    all_data = (
        SensorData.query
        # Orders by timestamp in descending order
        .order_by(SensorData.timestamp.desc())
        .limit(10)  # Limits the query to 10 results
        .all()
    )

    data_list = [
        {
            'id': data.id,
            'devicename': data.devicename,
            'pressure': data.pressure,
            'gyro': data.gyro,
            'leftdistance': data.leftdistance,
            'rightdistance': data.rightdistance,
            'temperature': data.temperature,
            'image': data.image,
            'is_flipped': data.is_flipped,
            'is_flipped_prob': data.is_flipped_prob,
            'is_eye_open': data.is_eye_open,
            'is_relayed': data.is_relayed,
            'timestamp': data.timestamp.isoformat(),
        } for data in all_data
    ]
    return jsonify(data_list)


@app.route('/baby/new', methods=['POST'])
def create_new_baby():
    # You can replace this with data from the request if needed
    data = request.get_json()
    new_baby = BabyData(
        **data
    )

    db.session.add(new_baby)
    db.session.commit()
    socketio.emit('new_profile', data)
    return jsonify({"result": "success"}), 201

@app.route("/baby/<int:baby_id>", methods=["GET"])
def get_baby(baby_id):
    # Query the BabyData model by baby_id
    baby = BabyData.query.filter_by(id=baby_id).first()

    # Check if the baby data exists
    if not baby:
        return jsonify({"error": "Baby data not found"}), 404

    # Use the to_dict() method to convert the baby data to a dictionary
    baby_data = baby.to_dict()

    # Return the baby data as JSON
    return jsonify({"baby": baby_data}), 200


@app.route("/user/<int:user_id>", methods=["GET"])
def get_user(user_id):
    # Query the User model by user_id
    user = User.query.filter_by(id=user_id).first()

    # Check if the user exists
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Create a dictionary to store the user data
    user_data = {
        "id": user.id,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "username": user.username,
        # We might want to exclude salt and password from the response
        # "salt": user.salt,
        # "password": user.password,
    }

    # Return the user data as JSON
    return jsonify({"user": user_data}), 200


@app.route("/user/register", methods=["POST"])
def register_user():
    data = request.get_json()
    # Check if all required fields are provided

    if not data:
        return jsonify({"error": "No data provided"}), 400

    # Extract the required fields from the JSON data
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    username = data.get("username")
    salt = data.get("salt")
    password = data.get("password")

    # Check if all required fields are provided
    if not all([first_name, last_name, username, salt, password]):
        return jsonify({"error": "Missing required field(s)"}), 400

    # Check if the username already exists
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({"error": "Username already exists"}), 400

    # Create a new user instance and add it to the database
    new_user = User(
        first_name=first_name,
        last_name=last_name,
        username=username,
        salt=salt,
        password=password
    )
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "User successfully registered", "user_id": new_user.id}), 201

@app.route("/user/<int:user_id>/babies", methods=["GET"])
def get_babies_by_user(user_id):
    # Query the BabyData model by user_id
    babies = BabyData.query.filter_by(user_id=user_id).all()

    # Check if any baby data exists for the given user_id
    if not babies:
        return jsonify({"error": "No baby data found for this user"}), 404

    # Use the to_dict() method to convert each baby data to a dictionary
    babies_data = [baby.to_dict() for baby in babies]

    # Return the babies data as JSON
    return jsonify({"babies": babies_data}), 200

@app.route("/user/<int:user_id>/baby/<int:baby_id>", methods=["GET"])
def get_baby_by_user_and_baby_id(user_id, baby_id):
    # Query the BabyData model by user_id and baby_id
    baby = BabyData.query.filter_by(user_id=user_id, id=baby_id).first()

    # Check if the baby data exists for the given user_id and baby_id
    if not baby:
        return jsonify({"error": "No baby data found for this user and baby ID combination"}), 404

    # Use the to_dict() method to convert the baby data to a dictionary
    baby_data = baby.to_dict()

    # Return the baby data as JSON
    return jsonify({"baby": baby_data}), 200

@app.route('/data/sensor/<fogName>', methods=['GET'])
def get_sensor_data_by_fog(fogName):
    start_time_str = request.args.get('start_time')
    end_time_str = request.args.get('end_time')
    reset = request.args.get('reset', 'false').lower() == 'true'
    print(f"{start_time_str} and {end_time_str}")

    # If start_time or end_time is not provided, use default values
    if start_time_str is not None:
        start_time = datetime.fromisoformat(start_time_str)
    else:
        # Set the default start time to one hour before the current time
        start_time = datetime.utcnow() - timedelta(hours=1)

    if end_time_str is not None:
        end_time = datetime.fromisoformat(end_time_str)
    else:
        # Set the default end time to the current time
        end_time = datetime.utcnow()

    # Fetch the data from the database based on the parameters
    data = fetch_sensor_data(fogName, start_time, end_time, reset)

    # Convert the data to JSON format and return it as a response
    return jsonify(data)

def fetch_sensor_data(fogName, start_time, end_time, reset):
    # Query the database to fetch sensor data based on the given parameters
    data_points = SensorData.query.filter(
        SensorData.devicename == fogName,
        SensorData.timestamp >= start_time,
        SensorData.timestamp <= end_time
    ).all()

    if reset:
        pass
        # Reset the data (if necessary)
        # Implement the reset functionality based on your requirements

    # Convert the data points to a JSON-friendly format
    data = []
    for data_point in data_points:
        data.append({
            'label': data_point.timestamp.isoformat(),
            'value': data_point.value
        })

    return data



def generate_fake_baby_data(device_id):
    first_name = fake.first_name()
    last_name = fake.last_name()
    age = fake.random_int(min=1, max=10)
    height = fake.pyfloat(min_value=2.0, max_value=5.0,
                          left_digits=1, right_digits=2)
    weight = fake.pyfloat(min_value=20.0, max_value=50.0,
                          left_digits=2, right_digits=2)
    image = None  # You can add image data if needed
    user_id = 1  # Replace this with a valid user ID from your database
    devicename = device_id

    user_data = BabyData(
        first_name=first_name,
        last_name=last_name,
        age=age,
        height=height,
        weight=weight,
        image=image,
        user_id=user_id,
        devicename=devicename
    )

    json_data = user_data.to_dict()

    return json_data


def send_fake_user_data(url, timeout):
    fake_user_data = {
        "first_name": fake.first_name(),
        "last_name": fake.last_name(),
        "username": fake.unique.user_name(),
        "salt": fake.pystr(min_chars=16, max_chars=16),
        "password": fake.password(length=12),
    }

    response = requests.post(url, json=fake_user_data)
    print(f"Sent fake user data: {fake_user_data} with {response}")
    time.sleep(timeout)


# For testing purposes, generate fake data
if __name__ == "__main__":
    with app.app_context():
        if not os.path.exists('sensor_data.db'):
            print("Creating database")
            db.create_all()

    from threading import Thread, Event
    import time

    url = "http://127.0.0.1:5000/data/sensor"
    url2 = "http://127.0.0.1:5000/baby/new"
    url3 = "http://127.0.0.1:5000/user/register"

    def send_fake_data(timeout, flag):
        while flag:
            with app.app_context():
                device_name = next(device_names)
                fake_data = generate_fake_data(device_name)
                response = requests.post(url, json=fake_data)
                print(f"Sent fake data: {fake_data} with {response}")
                time.sleep(timeout)
        # Run only once.
        if not flag:
            with app.app_context():
                device_name = next(device_names)
                fake_data = generate_fake_data(device_name)
                response = requests.post(url, json=fake_data)
                print(f"Sent fake data: {fake_data} with {response}")
                time.sleep(timeout)

    def send_fake_profile(timeout, flag):
        while flag:
            with app.app_context():
                device_name = next(device_names)
                fake_data = generate_fake_baby_data(device_name)
                response = requests.post(url2, json=fake_data)
                print(f"Sent fake profile: {fake_data} with {response}")
                time.sleep(timeout)
        # Run only once.
        if not flag:
            with app.app_context():
                device_name = next(device_names)
                fake_data = generate_fake_baby_data(device_name)
                response = requests.post(url2, json=fake_data)
                print(f"Sent fake profile: {fake_data} with {response}")
                time.sleep(timeout)

    def reset_database():
        while True:
            time.sleep(1800)  # 180 seconds is equivalent to 3 minutes
            with app.app_context():
                num_rows_deleted = db.session.query(SensorData).delete()
                db.session.commit()
                print(f"Deleted {num_rows_deleted} rows.")

    def send_alarm_event():
        while True:
            with app.app_context():
                socketio.emit('alarm_triggered', {
                              'message': 'Alarm triggered'})
                time.sleep(10000)


    def run_flask_app():
        # Start the Flask application
        app.run()

        # Start the Flask SocketIO application
        socketio.run(app)

    def setup():
        with app.app_context():
            send_fake_user_data(url3, 1)

            for i in range(5):
                send_fake_profile(0.5, flag=False)



    # Create an Event to signal when the Flask app has started
    app_started_event = Event()

    # Start the Flask app in a separate thread
    flask_app_thread = Thread(target=run_flask_app)
    flask_app_thread.start()

    # Wait for the Flask app to start
    time.sleep(5)
    app_started_event.set()

    # Now, you can be sure that the Flask app has started
    # You can start sending fake data to it

    # Start setup thread.
    Thread(target=setup).start()

    # Start sending fake data in a separate thread
    Thread(target=send_fake_data, args=(1, True)).start()

    # Start sending fake profile in a separate thread
    Thread(target=send_fake_profile, args=(100, True)).start()

    # Start resetting the database every 3 mins.
    Thread(target=reset_database).start()

    # Start sending the alarm event every 10 seconds
    Thread(target=send_alarm_event).start()  # New thread for the alarm event


