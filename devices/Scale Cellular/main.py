# Sensor Lab - Qwiic Scale

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
import qwiic_nau7802
from digi import cloud
import uio

__version__ = "1.2.0"
print(" Digi Sensor Lab - Scale v%s" % __version__)

# extend button class to check for initial calibration presses
class Button(sensorlab.Button): 
    def get(self): 
        return self.button.value()

# a button press at startup puts the scale into calibration mode
# USB connection and serial terminal access (console in XBee Studio for example) required for calibration
def calibrate(scale):    
    zero_offset = 0
    calibration_factor = 0
    
    print(" Set up scale with no weight on it. Press Enter when ready")
    input()
    dog.feed() # update watchdog timer

    # Calculate zero offset averaged over 64 readings
    scale.calculate_zero_offset(64)

    print(" Now place a known weight on the scale. When it's stable, enter the numerical weight in grams")
    user_input = input()
    weight = float(user_input)
    dog.feed() # update watchdog timer

    # Calculate calibration factor averaged over 64 readings
    scale.calculate_calibration_factor(weight, 64)
    zero_offset = scale.get_zero_offset()
    calibration_factor = scale.get_calibration_factor()

    print(" Calibration complete!")
    print(" Zero offset:", zero_offset)
    print(" Calibration factor:", calibration_factor)
    time.sleep(2)
    return (zero_offset, calibration_factor)

# non-volitile storage in file system for calibrations, so they survive power cycles
def get_calibration():
        print(" getting stored calibration...")
        try:
            calibrationFile = uio.open(config.CALIBRATION_FILE, mode="r") # check if file exists
        except OSError:
            # create file from config values if none present
            calibrationFile = uio.open(config.CALIBRATION_FILE, mode="w")
            # stored starter values
            calibrationFile.write(str(config.ZERO_OFFSET) + ',' + str(config.CALIBRATION_FACTOR) )
            calibrationFile.close()
            calibrationFile = uio.open(config.CALIBRATION_FILE, mode="r")
        # read calibrations from cached file
        zero_offset, calibration_factor = calibrationFile.readline().split(',')
        calibrationFile.close()
        print('', zero_offset, calibration_factor)
        return (float(zero_offset), float(calibration_factor))

# store calibrations in file system so they survive power cycles
def set_calibration(zero_offset, calibration_factor):
        print(' setting calibration')
        print('', zero_offset, calibration_factor)
        # open file for writing and save calibration values comma-separated
        calibrationFile = uio.open(config.CALIBRATION_FILE, mode="w")
        calibrationFile.write(str(zero_offset) + ',' + str(calibration_factor))
        calibrationFile.close()

# create module object for xbee
module=sensorlab.Module()
time.sleep(2) # wait for config to be applied
module.get_signal()

# create shutdown button and status led
button = Button(config.INPUT_BUTTON, module)
button.check(5000) # check for shutdown button
status_led = sensorlab.StatusLED(config.STATUS_LED)
status_led.off()

#create watchdog timer
dog = machine.WDT(timeout=90000, response=machine.HARD_RESET)

# set up sensor
try:
    scale = qwiic_nau7802.QwiicNAU7802()
    scale.begin()
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()
zero_offset, calibration_offset = get_calibration()
scale.set_zero_offset(zero_offset)
scale.set_calibration_factor(calibration_offset)

# initialize comms failure count
drm_fail = 0

print(' hold D0 button to begin new calibration...')
time.sleep(5)
if button.get() == 0:
    zero_offset, calibration_factor = calibrate(scale)
    set_calibration(zero_offset, calibration_factor)
    scale.set_zero_offset(zero_offset)
    scale.set_calibration_factor(calibration_factor)
else:
    print(' using existing calibration')

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), int(config.UPLOAD_RATE * -1000))
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
        t1 = time.ticks_ms()
        try:
            scale.begin()
            weight = round(scale.get_weight()) # floored at zero unlesss <allow_negative_weights = True>
        except Exception as e:
            print(e)
            status_led.blink(4, 1.5)
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM,weight)
            data.send(timeout=10)
            print(" drm -> ", weight)
            # print('zero_offset:', scale.get_zero_offset())
            # print('calibration_factor:', scale.get_calibration_factor())
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
