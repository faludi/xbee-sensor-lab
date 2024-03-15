# Sensor Lab - BLE Sensor

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

import binascii
from digi import ble
import struct
import time
import machine
import sensorlab
from digi import cloud
import config

__version__ = "1.0.1"
print(" Digi Sensor Lab - BLE Sensor v%s" % __version__)

# manages extracting the sensor data from the received BLE information
def get_characteristics_from_uuids(connection, service_uuid, characteristic_uuid):
    services = list(connection.gattc_services(service_uuid))
    if len(services):
        # Assume that there is only one service per UUID, take the first one
        my_service = services[0]
        characteristics = list(connection.gattc_characteristics(my_service, characteristic_uuid))
        return characteristics
    # Couldn't find specified characteristic, return an empy list
    return []


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

# set up BLE
address_type = ble.ADDR_TYPE_PUBLIC
# address into bytes object
address = binascii.unhexlify(config.THUNDERBOARD_ADDRESS.replace(':', ''))
# service and characteristic UUIDs
io_service_uuid = 0x1815
io_characteristic_uuid = 0x2A56
environment_service_uuid = 0x181A
temperature_characteristic_uuid = 0x2A6E
humidity_characteristic_uuid = 0x2A6F

# initialize comms failure count
drm_fail = 0

# activate BLE radio
active = ble.active(True)

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), config.UPLOAD_RATE * -1000)
# main loop
while True:
    try:
        print("Attempting connection to: {}".format(config.THUNDERBOARD_ADDRESS))
        with ble.gap_connect(address_type, address) as conn:
            print("connected")

            # There is only one temperature or humidity service and characteristic, so use the first and only one in the list
            temp_characteristic = get_characteristics_from_uuids(conn, environment_service_uuid, temperature_characteristic_uuid)[0]
            humid_characteristic = get_characteristics_from_uuids(conn, environment_service_uuid, humidity_characteristic_uuid)[0]


            # Blink the LED and read the temperature
            while True:
                    t2 = time.ticks_ms()
                    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
                        t1 = time.ticks_ms()
                        # read values
                        temperature = conn.gattc_read_characteristic(temp_characteristic)
                        humidity = conn.gattc_read_characteristic(humid_characteristic)
                        # Temperature value represented in 100th of a degree C
                        temperature = struct.unpack("h", temperature)[0] / 100.0
                        # print("T {:.2f} C ".format(temperature))
                        humidity = struct.unpack("h", humidity)[0] / 100.0
                        # print("H {:.2f} % ".format(humidity))
                        try:
                            data = cloud.DataPoints(config.DRM_TRANSPORT)
                            data.add(config.STREAM1,temperature)
                            data.send(timeout=10)
                            data = cloud.DataPoints(config.DRM_TRANSPORT)
                            data.add(config.STREAM2,humidity)
                            data.send(timeout=10)
                            print(" drm -> ", temperature, humidity)
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
                    
    except Exception as e:
        print('sensor not found: ', end='')
        print(e)
        button.check(5000) # check for shutdown button
        dog.feed() # update watchdog timer
