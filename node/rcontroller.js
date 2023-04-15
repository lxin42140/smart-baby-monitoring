let response = ""
let microbitDevices: string[] = []
let sensorValues: string[] = []
let state = 0
let commandStartTime = 0
let handshakeStartTime = 0
let data = ""

// radio settings
radio.setGroup(8)
radio.setTransmitSerialNumber(true)
radio.setTransmitPower(7)

// serial settings
serial.redirectToUSB()

// splash screen
basic.showIcon(IconNames.Yes)

/*
0 = initial state
1 = handshake
2 = send command to microbit
3 = pending receive sensor values from microbit
*/

basic.forever(function () {
    basic.showNumber(state)

    if (state == 1) {
        if (input.runningTime() - handshakeStartTime > 10000) {
            response = ""

            for (let microbitDevice of microbitDevices) {
                if (response.length > 0) {
                    response = "" + response + "," + microbitDevice
                } else {
                    response = microbitDevice
                }
            }

            // read to response in rhub.py to inform which microbit has connected
            serial.writeLine("enrol=" + response)
            state = 2
        }
    } else if (state == 3) {
        if (input.runningTime() - commandStartTime > 10000) {
            response = ""

            // concat all sensor values to a single string
            for (let sensorValue of sensorValues) {
                if (response.length > 0) {
                    response = "" + response + "," + sensorValue
                } else {
                    response = sensorValue
                }
            }

            serial.writeLine("" + response)
            // change state to send command again
            state = 2
        }
    }
})

// read data pushed from rhub.py
serial.onDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    data = serial.readLine()
    if (data == "handshake") {
        if (state == 0) {
            state = 1
            radio.sendString("handshake")
            handshakeStartTime = input.runningTime()
        }
    } else if (data.includes('cmd:')) {
        if (state == 2) {
            state = 3
            if (data.includes('cmd:sensor=')) {
                commandStartTime = input.runningTime()
                sensorValues = []
            }
            // send command to node
            radio.sendString("" + data.split(':')[1])
        }
        if (data.includes('cmd:alarm=')) {
            radio.sendString("" + data.split(':')[1])
        }
    } else if (data == "reset") {
        response = ""
        microbitDevices = []
        sensorValues = []
        state = 0
        commandStartTime = 0
        handshakeStartTime = 0
        data = ""
        radio.sendString("reset")
    }
})

// receive data from node
radio.onReceivedString(function (receivedString) {
    if (receivedString.includes('enrol=')) {
        if (state == 1) {
            microbitDevices.push(receivedString.split('=')[1])
        }
    } else if (receivedString.includes(':')) {
        if (state == 3) {
            // push received sensor value to array
            // format (from rnode.js) is "_:<value>,<value>"
            // push format <name>=<value>
            const receivedStringArr = receivedString.split(":")
            if (receivedStringArr[0] === "A") {
                const values = receivedStringArr[1].split(",")
                sensorValues.push(`pressure=${values[0]}`)
                sensorValues.push(`gyro=${values[1]}`)
            } else if (receivedStringArr[0] === "B1") {
                sensorValues.push(`leftdistance=${receivedStringArr[1]}`)
            } else if (receivedStringArr[0] === "B2") {
                sensorValues.push(`rightdistance=${receivedStringArr[1]}`)
            }
            
        }
    }
})
