# Slumber Watch

IoT project leveraging computer vision and data analytics to monitor baby sleeping position and sleeping patterns. 

SlumberWatch utilizes IoT technology and artificial intelligence to offer real-time monitoring and alerts for sleeping baby posture, the sleeping environment, and analytics of baby's sleeping patterns. It incorporates a variety of sensors such as gyroscope, pressure, image and ultrasonic distance to collect data on your baby's movements and sleeping patterns. Through the power of computer vision, data analytics, and supervised machine learning, the system can accurately detect when infant is at risk of rolling over and generate a real-time alarm to alert you to the danger.

## Requirements

Please perform the following set up

1. All development is done using virtual env. Please install virtualenv if you have not done so.
```
pip3 install virtualenv
which virtualenv -- verify installation
virtualenv venv -- create env called venv
source venv/bin/activate -- activate venv
pip install -r requirements.txt -- install packages to the virtual env
deactivate -- deactivate venv
sudo rm -rf venv -- remove env
```

2. Installation

2.1. To install the opencv model, you need to install the following packages

```
Please follow https://stackoverflow.com/questions/48734119/git-lfs-is-not-a-git-command-unclear

then
# Install git-lfs from https://git-lfs.github.com/
git clone https://github.com/opencv/opencv_zoo && cd opencv_zoo
git lfs install
git lfs pull
```

2.2. For detection of eye open/close, please download and unzip the following file, and place it under dir ml

```
http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
```

This is used in `ml > face_detection_model.detect_eye_in_image`

2.3. Install Cmake

for windows: install from https://cmake.org/download/
for mac: 
```
brew install cmake
```

3. Set up description

3.1 Microbit set up
1. transfer r-controller to one microbit
2. transfer rnode-baby to one microbit
3. transfer rnode-environment1 to one microbit
4. transfer rnode-environment2 to one microbit

3.2 Raspberry pi set up
1. install packages listed in requirements.txt, note that virtual env is not needed
2. run ./reset_db.sh to create the database tables
3. update the IP addresses in fog_processor.py

3.3 Cloud set up
1. create virtual env venv
2. install packages listed in requirements.txt
3. activate venv
4. run ./reset_db.sh to create the database tables
5. update the IP addresses in cloud_processor.py

3.4 FE set up
1. ensure that node is installed
2. go to frontend/my-app
3. run npm i

To run
1. in Raspberry pi, run fog_processor -> this will run all the programs
2. in local computer, run cloud_processor -> this will run all the programs
3. go to frontend/my-app and run npm run dev -> this will start frontend 