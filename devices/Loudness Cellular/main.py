# Sensor Lab - Loudness

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
from machine import I2C
import zio_loudness

__version__ = "1.2.1"
print(" Digi Sensor Lab - Loudness v%s" % __version__)

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
try:
    i2c = I2C(1)
    sensor = zio_loudness.ZioLoudness(i2c)
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
        try:
            loudness = sensor.get_loudness()
        except Exception as e:
            print(e)
            status_led.blink(4, 1.5)
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM,loudness)
            data.send(timeout=10)
            print(" drm -> ", loudness)
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
