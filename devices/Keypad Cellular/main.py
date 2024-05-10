# Sensor Lab - Keypad

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
import qwiic_keypad
from digi import cloud

__version__ = "1.2.1"
print(" Digi Sensor Lab - Keypad v%s" % __version__)

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
    keypad = qwiic_keypad.QwiicKeypad()
    keypad.begin()
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# initialize comms failure count
drm_fail = 0

# sending procedure functionalized for clarity
def send(value, drm_fail):
    try:
        data = cloud.DataPoints(config.DRM_TRANSPORT)
        data.add(config.STREAM,value)
        data.send(timeout=10)
        print(" drm -> ", value)
        drm_fail = 0
    except Exception as e:
        print(e)
        drm_fail += 1
        status_led.blink(2, 0.2)

# main loop
presses = ""
cnt = 0
active = False
t1 = time.ticks_ms() - (86400 * 1000)  # first upload immediately
print(" waiting for key presses...")
while True:
    try:
        keypad.update_fifo()
        keypress = keypad.get_button() # request a number from the keypad
        # print(keypress)
    except Exception as e:
        print(e)
        status_led.blink(4, 1.5)
    if ( ( ( keypress == ord('#') or keypress == ord('*') or ( active and ( time.ticks_diff(time.ticks_ms(), lastpress) > config.TIMEOUT * 1000 ) ) ) and cnt > 0 ) or cnt >= 9  ):
        print(chr(keypress))
        presses = int(presses)
        send(presses, drm_fail) # send as an integer
        active = False # reset user activity
        presses = "" # prep for new number
        cnt = 0
    elif keypress == 0:
        pass # no new keypad buttons pressed so do nothing
    elif keypress == -1:
        print( "keypad not found") # report known error
    elif keypress >= ord('0') and keypress <= ord('9'):
        print(chr(keypress))
        presses += chr(keypress) # append the key pressed to the value
        cnt += 1
        lastpress = time.ticks_ms() # note the time of last activity
        active = True # set user activity
    else:
        print(chr(keypress))
    time.sleep_ms(20)
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= 86400 * 1000: # heartbeat upload every 24 hours
        t1 = time.ticks_ms()
        send(-1, drm_fail) # send a negative one
    button.check(5000) # check for shutdown button
    if drm_fail >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}".format(drm=drm_fail))
        module.reset()
    dog.feed() # update watchdog timer
