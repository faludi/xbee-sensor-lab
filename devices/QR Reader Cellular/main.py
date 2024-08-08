# Sensor Lab - QR Reader https://www.sparkfun.com/products/23352

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
import qr_reader_qwiic
from machine import I2C
from digi import cloud

__version__ = "1.0.0"
print(" Digi Sensor Lab - QR Reader v%s" % __version__)

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
    qr_reader = qr_reader_qwiic.QR_READER(i2c)
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# initialize comms failure count
drm_fail = 0

# initialize temporary storage of prior reads
last_message = ''
message = None

t1 = time.ticks_ms() # mark start of process
# main loop
while True:
    try:
        message = qr_reader.get_data()
    except Exception as e:
        print(e)
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.TIMEOUT_RATE * 1000: # time to clear last message
        last_message = ''
        t1 = time.ticks_ms()
        print('.', end='')
    if message is not None and message != last_message:
        t1 = time.ticks_ms() # mark the time of latest upload
        last_message = message # update the last message sent
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM1,message)
            data.send(timeout=10)
            print('')
            print(" drm -> ", message)
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
    time.sleep(qr_reader_qwiic.TINY_CODE_READER_DELAY)
