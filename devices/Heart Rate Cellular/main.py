# Sensor Lab - Heart Rate MAX30101 https://www.sparkfun.com/products/16474

'''
 Copyright 2023, Digi International Inc.

This Source Code Form is subject to the terms of the Mozilla Public
License, v. 2.0. If a copy of the MPL was not distributed with this
file, you can obtain one at http://mozilla.org/MPL/2.0/.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF 
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR 
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES 
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN 
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF 
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
'''

import sensorlab
import time
import config
import machine
import qwiic_max3010x
from digi import cloud

__version__ = "1.1.0"
print(" Digi Sensor Lab - Heart Rate v%s" % __version__)

# obtain raw sensor data and calculations for measuring heart rate
class HeartRate():

    RATE_SIZE = 10 # Increase this for more averaging. 4 is good.
    rates = list(range(RATE_SIZE)) # list of heart rates
    for rate in range(RATE_SIZE): # initialize with reasonable defaults
        rates[rate]=60
    rateSpot = 0
    lastBeat = 0 # Time at which the last beat occurred
    beatsPerMinute = 0.00
    beatAvg = 0
    samplesTaken = 0 # Counter for calculating the Hz or read rate
    
    def __init__(self, heart_sensor):
        self.heart_sensor = heart_sensor
        self.startTime = self.millis() # Used to calculate measurement rate
        self.finalBeat = 0

    def millis(self):
        return time.ticks_ms()

    def measure_bpm(self):
        beats = 0
        while True:

            irValue = self.heart_sensor.getIR()
            self.samplesTaken += 1
            if self.heart_sensor.checkForBeat(irValue) == True:
                # We sensed a beat!
                beats += 1
                delta = ( self.millis() - self.lastBeat )
                self.lastBeat = self.millis()	
                if beats > 2:
                    print('BEAT ', end='')

                    self.beatsPerMinute = 60 / (delta / 1000.0)
                    self.beatsPerMinute = round(self.beatsPerMinute,1)
                    print(self.beatsPerMinute)

                    if self.beatsPerMinute < 255 and self.beatsPerMinute > 20:
                        self.rateSpot += 1
                        self.rateSpot %= self.RATE_SIZE # Wrap variable
                        self.rates[self.rateSpot] = self.beatsPerMinute # Store this reading in the array

                        # Take average of readings
                        self.beatAvg = 0
                        for x in range(0, self.RATE_SIZE):
                            self.beatAvg += self.rates[x]
                        self.beatAvg /= self.RATE_SIZE
                        self.beatAvg = round(self.beatAvg)
            
            Hz = round(float(self.samplesTaken) / ( ( self.millis() - self.startTime ) / 1000.0 ) , 2)
            if (self.samplesTaken % 250 ) == 0:
                return (self.beatAvg, self.beatsPerMinute, irValue, Hz)


# create module object for xbee
module=sensorlab.Module()
time.sleep(2) # wait for config to be applied
module.get_signal()

# create shutdown button and status led
button = sensorlab.Button(config.INPUT_BUTTON, module)
button.check(5000) # check for shutdown button
status_led = sensorlab.StatusLED(config.STATUS_LED)
status_led.off()

#create watchdog timer
dog = machine.WDT(timeout=90000, response=machine.HARD_RESET)

# set up sensor
try:
    heart_sensor = qwiic_max3010x.QwiicMax3010x()
    if heart_sensor.begin() == False:
        print("Qwiic MAX3010x not connected")
    else:
        print("Qwiic MAX3010x connected")

    if heart_sensor.setup() == False:
        print("Qwiic MAX3010x setup failure")
    else:
        print("Setup complete.")
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

heart_sensor.setPulseAmplitudeRed(0) # Turn Red LED off
heart_sensor.setPulseAmplitudeGreen(0x80) # Turn on Green LED medium

# intialize heart rate calculation
heartrate = HeartRate(heart_sensor)

# initialize comms failure count
drm_fail = 0

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), config.UPLOAD_RATE * -1000)
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
        t1 = time.ticks_ms()
        try:
            readings = heartrate.measure_bpm()
            print ('readings: beat avg: {bavg}  beat rate: {brate}  IR value: {ir}  ' \
                    'Hz: {hertz}'.format(bavg = readings[0], brate = readings[1], ir = readings[2], hertz = readings[3]))
            bpm = readings[0]
            ir = readings[2]
            if ir < 90000: # values are typically over 100,000 when a finger is placed
                    bpm = -1
        except Exception as e:
            print(e)
            status_led.blink(4, 1.5)
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM,bpm)
            data.send(timeout=10)
            print(" drm -> ", bpm)
            drm_fail = 0
        except Exception as e:
            print(e)
            drm_fail += 1
            status_led.blink(2, 0.2)
    button.check(5000) # check for shutdown button
    if drm_fail >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}".format(drm=drm_fail))
        module.reset()
    dog.feed() # update watchdog timer
