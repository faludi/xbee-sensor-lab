# Sensor Lab - BLE Scanner

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

import iBeacon
import binascii
from digi import ble
import time
import alphanum_qwiic
import machine
import sensorlab
import config
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
print(" Digi Sensor Lab - BLE Scanner v%s" % __version__)

def form_mac_address(addr: bytes) -> str:
    return ":".join('{:02x}'.format(b) for b in addr)

# extends sensorlab class for safe shutdown of BLE advertising
class Button(sensorlab.Button):

    def check(self, press_time=5000):
        startTime = time.ticks_ms()
        while self.button.value() == 0:
            if time.ticks_ms() - startTime > press_time:
                print("stopping BLE...")
                ble.gap_advertise(None)
                print("BLE beacon ended")
                print("shutting down cell module...")
                self.module.shutdown()
                if 'display' in locals(): # if display has been defined
                    display.print("OFF")
                print("shutdown complete")
                raise SystemExit(0)

# manages distance calculation with smoothing and text labels           
class Distance_Data():

    def __init__(self, array_size=10):
        self.array_size = array_size
        self.distance_array = []
        self.distance_avg = 0

    def update(self,distance):
        while len(self.distance_array) >= self.array_size:
            self.distance_array.pop(0)
        self.distance_array.append(distance)
        for item in self.distance_array:
            self.distance_avg += item
        self.distance_avg = self.distance_avg / len(self.distance_array)
        return self.distance_avg
    
    def get(self):
        return self.distance_avg


def get_label(distance):
    if distance is None:
        label = "NONE"
    elif 0 <= distance <= 1:
        label = "HERE"
    elif 1 < distance <= 3:
        label = "NEAR"
    elif 3 < distance <= 7:
        label = "MED"
    elif 7 < distance < 1000:
        label = "FAR"
    else:
        label = "OUT OF RANGE"
    return label

def scan_for_iBeacon_frames(duration_ms: int):

    # Configure scan for the entire window
    with ble.gap_scan(duration_ms=duration_ms, interval_us=4500, window_us=4500) as scan:

        iBeacon_count = 0
        beacon_count = 0
        distance_accumulator = 0
        rssi_accumulator = 0

        while not scan.stopped():

            for frame in scan.get():

                beacon_count += 1
                payload = frame['payload']

                if iBeacon.is_proximity_beacon(payload):
                    (uuid, power, major, minor) = iBeacon.parse_proximity_beacon(payload)
                    if  (major == 44 and minor == 47):  # check for XBee beacon
                        # Calculate approximate distance
                        calib_rssi = power - 256
                        rssi = frame['rssi']
                        db_ratio = float(calib_rssi - rssi)
                        linear_ratio = 10.0 ** (db_ratio / 10.0)
                        distance = linear_ratio ** 0.5

                        addr = binascii.hexlify(frame['address']).decode()
                        uuid = binascii.hexlify(uuid).decode()
                        print('.', end='')
                        # print("iBeacon from {}".format(addr))
                        # print("UUID={} major={} minor={}".format(uuid, major, minor))
                        # print("RSSI={} calibrated_RSSI={}".format(rssi, calib_rssi))
                        # print("distance={:0.2f} meters".format(distance))
                        iBeacon_count += 1
                        distance_accumulator += distance
                        rssi_accumulator += rssi
    print('')
    time.sleep(0.2)
    print("{} iBeacon frames of total {} beacon frames".format(iBeacon_count, beacon_count))
    if iBeacon_count > 0:
        distance_avg = distance_accumulator / iBeacon_count
        rssi_avg = rssi_accumulator / iBeacon_count
        return (distance_avg, rssi_avg)
    else:
        return(None, None)


# create module object for xbee
module=sensorlab.Module()
time.sleep(2) # wait for config to be applied
module.get_signal()

# create shutdown button and status led
button = Button(config.INPUT_BUTTON, module)
button.check(5000) # check for shutdown button
status_led = sensorlab.StatusLED(config.STATUS_LED)
status_led.off()

# create mqtt client and connect to server
if config.MQTT_UPLOAD:
    client = MQTTClient(config.MQTT_CLIENT_ID+module.get_iccid(), config.MQTT_SERVER, port=config.MQTT_PORT, 
                        user=secrets.MQTT_USER, password=secrets.MQTT_PASSWORD, ssl=config.MQTT_SSL)
    print(" connecting to '%s'... " % config.MQTT_SERVER, end="")
    try:
        client.connect()
        print(" connected")
    except Exception as e:
        print(e)
        status_led.blink(10, 0.5)
        print(" mqtt connection failed")

#create watchdog timer
dog = machine.WDT(timeout=90000, response=machine.HARD_RESET)

# set up display
try:
    i2c = machine.I2C(1, freq=config.FREQ)
    display = alphanum_qwiic.ALPHANUM_QWIIC(i2c)
    display.set_blink_rate(0)  # no blinking
    display.set_brightness(10) # range: 0 to 15
except OSError as e:
    print(' display not found error:', e)

# initialize comms failure count
drm_fail = mqtt_fail = http_fail = 0

#initialize distance data with list size
data_array_size = 6
distance_data = Distance_Data(data_array_size)
average_distance = -1
no_signal = 0
sample_cycles = 5
label = 'NONE'

# activate BLE radio
active = ble.active(True)

# Print out the BLE Mac
print("Started Bluetooth with address of: {}".format(form_mac_address(ble.config("mac"))))
if 'display' in locals(): # check if display has been defined
    display.print_scroll(("BLE SCAN v" + __version__), 0.6, 0.3)
    time.sleep(0.5)
    display.print(" -- ")

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), int(config.UPLOAD_RATE * -1000))
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
        t1 = time.ticks_ms()
        
        for sample in range(sample_cycles):
            try:
                distance, rssi = scan_for_iBeacon_frames(2_000)
            except Exception as e:
                print(e)
            if distance is None:
                no_signal += 1
                if 'display' in locals(): # if display has been defined
                    try:
                        display.set_decimal(True)
                    except:
                        pass
                    time.sleep(0.5)
                    try:
                        display.set_decimal(False)
                    except:
                        pass
            else:
                no_signal = 0
                average_distance = distance_data.update(distance)
                label = get_label(average_distance)
                print(get_label(average_distance))
                
        if no_signal > sample_cycles:
                label = "NONE"
        if 'display' in locals(): # if display has been defined
            try:
                display.print_scroll((label), 0.6, 0.3)
            except Exception as e:
                    print(e)
        if config.HTTP_UPLOAD:
            try:
                json = {"variable":config.HTTP_VARIABLE1,"value":label,"unit":config.HTTP_UNIT1}
                response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
                print(" http -> " , label," (" + str(response.status_code), response.reason.decode(), 
                      "|", str(time.ticks_diff(time.ticks_ms(), t1)/1000), "secs)")
                if 200 <= response.status_code <= 299:
                    http_fail = 0
                else:
                    http_fail +=1
            except Exception as e:
                print(e)
                http_fail += 1
                status_led.blink(2, 0.2)
            finally:
                response.close()
        if config.MQTT_UPLOAD:
            try:
                client.publish(config.MQTT_TOPIC1, str(label))
                print(" mqtt -> ", label)
                mqtt_fail = 0
            except Exception as e:
                print(e)
                mqtt_fail += 1
                status_led.blink(2, 0.2)
        if config.DRM_UPLOAD:
            try:
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM1, label)
                data.send(timeout=10)
                # data = cloud.DataPoints(config.DRM_TRANSPORT)
                # data.add(config.STREAM2, average_distance)
                # data.send(timeout=10)
                print(" drm -> ", label)
                drm_fail = 0
            except Exception as e:
                print(e)
                drm_fail += 1
                status_led.blink(2, 0.2)
    button.check(5000) # check for shutdown button
    if max(drm_fail,mqtt_fail,http_fail) >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}, mqtt_fails {mqtt}, http_fails {http}".format(drm=drm_fail, mqtt=mqtt_fail, http=http_fail, ))
        module.reset()
    dog.feed() # update watchdog timer
