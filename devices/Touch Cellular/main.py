# Sensor Lab - Touch CAP1203  https://www.sparkfun.com/products/15344

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
import qwiic_cap1203
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
print(" Digi Sensor Lab - Touch v%s" % __version__)

# create module object for xbee
module=sensorlab.Module()
time.sleep(2) # wait for config to be applied
module.get_signal()

# create shutdown button and status led
button = sensorlab.Button(config.INPUT_BUTTON, module)
button.check(5000) # check for shutdown button
status_led = sensorlab.StatusLED(config.STATUS_LED)
status_led.off()

# create mqtt client and connect to server
if config.MQTT_UPLOAD:
    client = MQTTClient(config.MQTT_CLIENT_ID+module.get_iccid(), config.MQTT_SERVER, port=config.MQTT_PORT, 
                        user=secrets.MQTT_USER, password=secrets.MQTT_PASSWORD, ssl=config.MQTT_SSL)
    print(" connecting to '%s'... " % config.MQTT_SERVER, end="")
    client.connect()
    print(" connected")

#create watchdog timer
dog = machine.WDT(timeout=90000, response=machine.HARD_RESET)

# set up sensor
try:
    touch_sensor = qwiic_cap1203.QwiicCAP1203()
    touch_sensor.begin()
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# initialize comms failure count
comm_fail  = 0

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), int(config.UPLOAD_RATE * -1000))
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
        t1 = time.ticks_ms()
        try:
            left_status = touch_sensor.is_left_touched()
            middle_status = touch_sensor.is_middle_touched()
            right_status = touch_sensor.is_right_touched()
            print("Touch Pad Status: " + str(left_status) + "  " + str(middle_status) + "  " + str(right_status))
            touch = (left_status) + (middle_status << 1) + (right_status << 2)
        except Exception as e:
            print(e)
            status_led.blink(4, 1.5)
        if config.HTTP_UPLOAD:
            try:
                json = {"variable":config.HTTP_VARIABLE,"value":touch,"unit":config.HTTP_UNIT}
                response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
                print(" http -> " , touch," (" + str(response.status_code), response.reason.decode(), 
                      "|", str(time.ticks_diff(time.ticks_ms(), t1)/1000), "secs)")
                if 200 <= response.status_code <= 299:
                    comm_fail = 0
                else:
                    comm_fail +=1
            except Exception as e:
                print(e)
                comm_fail += 1
                status_led.blink(2, 0.2)
            finally:
                response.close()
        if config.MQTT_UPLOAD:
            try:
                client.publish(config.MQTT_TOPIC, str(touch))
                print(" mqtt -> ", touch)
                comm_fail = 0
            except Exception as e:
                print(e)
                comm_fail += 1
                status_led.blink(2, 0.2)
        if config.DRM_UPLOAD:
            try:
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM,touch)
                data.send(timeout=60)
                print(" drm -> ", touch)
                comm_fail  = 0
            except Exception as e:
                print(e)
                comm_fail  += 1
                status_led.blink(2, 0.2)
    button.check(5000) # check for shutdown button
    if comm_fail  >= config.MAX_COMMS_FAIL:
        print (" comm_fails {comm}".format(comm=comm_fail ))
        module.reset()
    dog.feed() # update watchdog timer
