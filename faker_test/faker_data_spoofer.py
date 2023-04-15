import random
import base64
import io
from itertools import cycle
from faker import Faker
from PIL import Image

fake = Faker()
fake_server = ""
url = f"{fake_server}/data/sensor"


device_names = cycle(['Device1', 'Device2', 'Device3', 'Device4', 'Device5'])

def generate_fake_data(device_name):
    image_data = generate_fake_image()
    return {
        'devicename': device_name,
        'pressure': random.randint(50, 150),
        'gyro': random.randint(30, 70),
        'leftdistance': random.randint(1, 10),
        'rightdistance': random.randint(1, 10),
        'temperature': random.randint(20, 30),
        'image': image_data,
        'is_flipped': random.choice([0, 1]),
        'is_flipped_prob': random.uniform(0, 1),
        'is_eye_open': random.choice([0, 1]),
        'is_relayed': random.choice([0, 1])
    }

def generate_random_color():
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

def generate_fake_image(width=100, height=100):
    image = Image.new("RGB", (width, height))

    for x in range(width):
        for y in range(height):
            image.putpixel((x, y), generate_random_color())

    buffer = io.BytesIO()
    image.save(buffer, "JPEG")
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

