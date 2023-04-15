let commandKey = ""
let commandValue = ""
let state = 0
// led settings
let ledState = 0
let lastBlinkTime = 0;
let showBlink = true;
// radio settings
let randomWaitPeriod = 0
radio.setGroup(8)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(7)
//pins
let pressureSensorPin = AnalogPin.P1
let ultrasonicAPin = DigitalPin.P1
let ultrasonicBPin = DigitalPin.P2

// splash screen
basic.showIcon(IconNames.Yes)

basic.forever(function () {
  basic.clearScreen();
  showConnectionStatus();
})

/**
LED coordinate

(0,0) (1,0) (2,0) (3,0) (4,0)

(0,1) (1,1) (2,1) (3,1) (4,1)

(0,2) (1,2) (2,2) (3,2) (4,2)

(0,3) (1,3) (2,3) (3,3) (4,3)

(0,4) (1,4) (2,4) (3,4) (4,4)
 */

function showConnectionStatus() {
  if (state == 1) {
    for (let i = 0; i <= 4; i++) {
      led.plot(4, i);
    }
  } else {
    for (let i = 0; i <= 4; i++) {
      led.unplot(4, i);
    }
  }
}

/**
state
    0 = initial
    1 = handshake / command / connected
*/

// random wait to avoid replying at the same time which can cause concurrency issues
function randomWait() {
  randomWaitPeriod = Math.randomRange(100, 9900)
  basic.pause(randomWaitPeriod)
}

radio.onReceivedString(function (receivedString) {
  if (receivedString == "handshake") {
    if (state == 0) {
      state = 1
      randomWait()
      radio.sendString("enrol=" + control.deviceName())
    }
  } else if (receivedString == "reset") {
    // requires new handshake
    commandKey = ""
    commandValue = ""
    randomWaitPeriod = 0
    state = 0
  } else {
    if (state == 1) {
      let tempArray = receivedString.split('=')
      commandKey = tempArray[0]
      commandValue = tempArray[1]

      if (commandKey == "sensor") {
        if (commandValue == "all") {
          randomWait()
          getBabyData();
        }
      }
    }
  }
})

//pressure, roll
function getBabyData() {
  //send pressure[4], roll[3]
  let roll = Math.abs(input.rotation(Rotation.Roll));
  let pressure = pins.analogReadPin(pressureSensorPin);
  radio.sendString(`A:${pressure},${roll}`)
}
