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
import uio

__version__ = "1.1.0"
print(" Digi Sensor Lab - BLE Sensor v%s" % __version__)

def form_mac_address(addr: bytes) -> str:
    return ":".join('{:02x}'.format(b) for b in addr)

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

# non-volitile storage in file system for sensor's MAC address, so it survives power cycles
def get_address():
        print(" getting stored sensor address...")
        try:
            addressFile = uio.open(config.SENSOR_ADDRESS_FILE, mode="r") # check if file exists
        except OSError:
            # create file with a zero address if none present
            addressFile = uio.open(config.SENSOR_ADDRESS_FILE, mode="w")
            # stored starter values
            addressFile.write('00:00:00:00:00:00')
            addressFile.close()
            addressFile = uio.open(config.SENSOR_ADDRESS_FILE, mode="r")
        # read coordinates from cached file and send
        sensor_address = addressFile.readline()
        addressFile.close()
        print(' sensor address from file:', sensor_address)
        address = binascii.unhexlify(sensor_address.replace(':', ''))
        return address

# store sensor address in file system so it survives power cycles
def set_address(sensor_address):
        print(' setting sensor address')
        print('', sensor_address)
        # open file for writing and save lat/long comma-separated
        addressFile = uio.open(config.SENSOR_ADDRESS_FILE, mode="w")
        addressFile.write(str(sensor_address))
        addressFile.close()


# discover sensor address using gatt scan for payloads containing "Thunderboard"
def discover_address():
    # scan with a context manager
    with ble.gap_scan(5000, interval_us=50000, window_us=50000) as scanner:
        # Loop through the available advertisements, blocking if there are none. Exits when the scan stops.
        for advertisement in scanner:
            if b'Thunderboard' in advertisement['payload']:   # this will find any Thunderboard
                discovered_address = advertisement['address']
                print(" found Thunderboard with address of: {}".format(form_mac_address(discovered_address)))
                set_address(form_mac_address(discovered_address))
                return discovered_address
    print(' no Thunderboards found, retaining existing address...')
    return address


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
address = get_address()                #binascii.unhexlify(config.THUNDERBOARD_ADDRESS.replace(':', ''))
# service and characteristic UUIDs
io_service_uuid = 0x1815
io_characteristic_uuid = 0x2A56
environment_service_uuid = 0x181A
temperature_characteristic_uuid = 0x2A6E
humidity_characteristic_uuid = 0x2A6F

# initialize comms failure count
drm_fail = 0
ble_fail = 0

# activate BLE radio
active = ble.active(True)

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), config.UPLOAD_RATE * -1000)
# main loop
while True:
    print(' current sensor address:', form_mac_address(address))
    if ble_fail < config.MAX_BLE_FAIL:
        try:
            print(' connecting to:', form_mac_address(address))
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
                            ble_fail = 0
                    
        except Exception as e:
            print('sensor not found: ', end='')
            print(e)
            ble_fail += 1
            button.check(5000) # check for shutdown button
            dog.feed() # update watchdog timer
    else:
        if config.AUTO_DISCOVERY:
            print (" ble_fails {ble}".format(ble=ble_fail))
            print(' discovering address...')
            address = discover_address()
        ble_fail = 0

    dog.feed() # update watchdog timer
