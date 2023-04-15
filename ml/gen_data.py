import random
import datetime

if __name__ == '__main__':
    i = 0    
    while i < 50:
        eye_open = 0
        pressure = random.randint(901, 1023)
        gyro = random.randint(0, 90)
        left_distance = random.randint(300, 350)
        right_distance = random.randint(300, 350)
        # generate timestamp in format of 2022-03-30 10:00:00
        timestamp = datetime.datetime(2022, 3, 30, 10, 0, 0) + datetime.timedelta(seconds=i*10)

        record = f"{eye_open},{pressure},{gyro},{left_distance},{right_distance},{timestamp}"
        print(record)

        i += 1

    while i < 100:
        eye_open = 1
        pressure = random.randint(0, 1023)
        gyro = random.randint(0, 180)
        left_distance = random.randint(3, 350)
        right_distance = random.randint(3, 350)
        # generate timestamp in format of 2022-03-30 10:00:00
        timestamp = datetime.datetime(2022, 3, 30, 10, 0, 0) + datetime.timedelta(seconds=i*10)

        record = f"{eye_open},{pressure},{gyro},{left_distance},{right_distance},{timestamp}"
        print(record)

        i += 1
