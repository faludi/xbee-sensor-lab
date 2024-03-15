#
# DEVELOPER IS RESPONSIBLE FOR OBTAINING THE NECESSARY LICENSES FROM APPLE.
#
# iBeacon(TM) is a trademark of Apple Inc. and use of this code must comply with
# their licence.
#

# Copyright (c) 2019, Digi International, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import iBeacon
import time
import binascii
from digi import ble
from machine import Pin


def form_mac_address(addr: bytes) -> str:
    return ":".join('{:02x}'.format(b) for b in addr)

# button class added to generic sample for safe shutdown
class Button:
    def __init__(self, pin):
        self.pin = pin
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)

    def check(self, press_time=5000):
        startTime = time.ticks_ms()
        while self.button.value() == 0:
            if time.ticks_ms() - startTime > press_time:
                print("shutting down cell module...")
                # Stop advertising
                ble.gap_advertise(None)
                print("BLE beacon ended")
                raise SystemExit(0)

button = Button("D0")


# Make sure the BLE radio is on
active = ble.active(True)
# Print out the BLE Mac
print("Started Bluetooth with address of: {}".format(form_mac_address(ble.config("mac"))))

# iBeacon frame parameters
uuid = binascii.unhexlify('b7a8bf1d-f5bd-4b57-9b35-12c7be74eb7a'.replace('-', ''))  # Randomly generated UUID
major = 44
minor = 47
rssi = -45
calib_power = 256 - abs(rssi)  # Calibrated power 1 meter away [enter values as 256 - positive RSSI value] # (was 189)

# Create the iBeacon frame
frame = iBeacon.make_proximity_beacon(uuid, calib_power, major, minor)

# Advertise the iBeacon frame every 200ms
interval_us = 200_000
ble.gap_advertise(interval_us, frame)
print("BLE beacon started...")

while True:
    button.check(5000) # check for shutdown button