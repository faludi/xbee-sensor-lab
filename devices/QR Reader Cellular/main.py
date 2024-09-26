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
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
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

# create mqtt client and connect to server
if config.MQTT_UPLOAD:
    client = MQTTClient(config.MQTT_CLIENT_ID+module.get_iccid(), config.MQTT_SERVER, port=config.MQTT_PORT, 
                        keepalive=120, user=secrets.MQTT_USER, password=secrets.MQTT_PASSWORD, ssl=config.MQTT_SSL)
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

# set up sensor
try:
    i2c = I2C(1, freq=400000)
    qr_reader = qr_reader_qwiic.QR_READER(i2c)
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# initialize comms failure count
drm_fail = mqtt_fail = http_fail = 0

# initialize temporary storage of prior reads
last_message = ''
message = None

t1 = t3 = time.ticks_ms() # mark start of process
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
        if config.HTTP_UPLOAD:
            try:
                json = {"variable":config.HTTP_VARIABLE,"value":message,"unit":config.HTTP_UNIT}
                response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
                print(" http -> " , message," (" + str(response.status_code), response.reason.decode(), 
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
                client.publish(config.MQTT_TOPIC, str(message))
                print(" mqtt -> ", message)
                mqtt_fail = 0
            except Exception as e:
                print(e)
                mqtt_fail += 1
                status_led.blink(2, 0.2)
        if config.DRM_UPLOAD:
            try:
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM1,message)
                data.send(timeout=10)
                print('')
                print(" drm -> ", message)
                drm_fail  = 0
            except Exception as e:
                print(e)
                drm_fail  += 1
                status_led.blink(2, 0.2)
    if config.MQTT_UPLOAD:
        if time.ticks_diff(t2, t3) >= 60 * 1000: # ping mqtt every 60 seconds
            t3 = time.ticks_ms()
            client.ping() # send a ping to the mqtt server
    button.check(5000) # check for shutdown button
    if max(drm_fail,mqtt_fail,http_fail) >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}, mqtt_fails {mqtt}, http_fails {http}".format(drm=drm_fail, mqtt=mqtt_fail, http=http_fail, ))
        module.reset()
    dog.feed() # update watchdog timer
    time.sleep(qr_reader_qwiic.TINY_CODE_READER_DELAY)
