from picamera import PiCamera
from time import sleep
import sqlite3
from datetime import datetime

camera = PiCamera()
def captureImage(directoryToSave):
    camera.start_preview()
    sleep(2) # 2 seconds for light capture
    #capture and store on desktop temporarily
    imagePath = directoryToSave + "/camera-{}.jpg".format(datetime.today())
    camera.capture(imagePath)
    print("captured")
    binaryImage = convertToBinaryData(imagePath)
    return binaryImage


def convertToBinaryData(filePath):
    with open(filePath, 'rb') as file:
        file = file.read()
    return sqlite3.Binary(file)
