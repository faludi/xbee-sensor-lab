# Sensor Lab - Person Sensor

'''
 Copyright 2024, Digi International Inc.

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
import person_sensor_qwiic
from machine import I2C
from digi import cloud

__version__ = "1.0.2"
print(" Digi Sensor Lab - Person Sensor v%s" % __version__)

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
    i2c = I2C(1, freq=400000)
    person_sensor = person_sensor_qwiic.person_sensor(i2c)
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# initialize comms failure count
drm_fail = 0

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), config.UPLOAD_RATE * -1000)
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
        t1 = time.ticks_ms()
        faces = 0
        is_facing = []
        while (time.ticks_ms() < t1 + (config.UPLOAD_RATE * 1000) - (1 * 1000)): # until one second before the end of the cycle...
            try:
                num_faces, faces_data = person_sensor.get_data() # get number of faces detected and the data about each
                if (num_faces > faces):
                    faces = num_faces # record the max number of faces detected
                for face_record in faces_data:
                    is_facing.append(face_record['is_facing']) # for each face, record facing status in array              
            except Exception as e:
                print(e)
                num_faces = 0 # if sensor is not found then face count is zero
                status_led.blink(4, 1.5)
            try:
                attention = sum(is_facing)/len(is_facing) # average the is_facing to determine percentage of attention
            except ZeroDivisionError:
                attention = 0.0 # if no faces found, set attention to zero
            if num_faces > 0: # print a progress string for debugging detection
                print(num_faces,end='')
            else:
                print('.',end='')
            time.sleep(0.2) # wait 200 ms between reads
        print('') # line feed
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM1,faces)
            data.send(timeout=10)
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM2,attention)
            data.send(timeout=10)
            print(" drm -> ", faces, attention)
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
