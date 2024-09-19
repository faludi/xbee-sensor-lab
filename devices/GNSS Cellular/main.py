# Sensor Lab - GNSS

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
from digi import cloud
from digi import gnss
import uio

__version__ = "1.2.1"
print(" Digi Sensor Lab - GNSS v%s" % __version__)

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

# set up and test for sensor.
# GNSS sensor is native. Note that LTE cannot run during GNSS polling

# initialize comms failure count
drm_fail = 0

# set initial upload rate
upload_rate = config.UPLOAD_RATE

def location_cb(location):
    global upload_rate
    if location is None:
        print(" GNSS lookup failed")
        try:
            latlongFile = uio.open(config.LAT_LONG_FILE, mode="r") # check if file exists
        except OSError:
            # create file with Digi HQ coordinates if none present
            latlongFile = uio.open(config.LAT_LONG_FILE, mode="w")
            latlongFile.write("44.9265206,-93.3977228") # Digi International Headquarters
            latlongFile.close()
            latlongFile = uio.open(config.LAT_LONG_FILE, mode="r")
        # read coordinates from cached file and send
        lat, long = latlongFile.readline().split(',')
        latlongFile.close()
        print(lat, long, 1)
        send(lat, long, 1)
        upload_rate = config.UPLOAD_RATE * 2
    else:
        print(' GNSS received')
        print(location["latitude"], location["longitude"], 0)
        send(location["latitude"], location["longitude"], 0)
        # open file for writing and save lat/long comma-separated
        latlongFile = uio.open(config.LAT_LONG_FILE, mode="w")
        latlongFile.write(str(location["latitude"]) + ',' + str(location["longitude"]))
        latlongFile.close()
        upload_rate = config.UPLOAD_RATE

# sending procedure functionalized for clarity
def send(value1, value2, value3):
        global drm_fail
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM1,value1)
            data.send(timeout=10)
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM2,value2)
            data.send(timeout=10)
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM3,value3)
            data.send(timeout=10)
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM4,"(" + value1 + "," + value2 + ")")
            data.send(timeout=10)
            print(" drm -> ", value1, value2, value3)
            drm_fail = 0
        except Exception as e:
            print(e)
            drm_fail += 1
            status_led.blink(2, 0.2)


# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), int(upload_rate * -1000))
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= upload_rate * 1000: # time for a sample
        t1 = time.ticks_ms()
        try:
            print(" requesting GNSS...")
            gnss.single_acquisition(location_cb, 50)
        except Exception as e:
            print(e)
    button.check(5000) # check for shutdown button
    if drm_fail >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}".format(drm=drm_fail))
        module.reset()
    dog.feed() # update watchdog timer
