# Sensor Lab - Air Quality SGP40 https://www.sparkfun.com/products/18345

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
import qwiic_sgp40
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
print(" Digi Sensor Lab - Air Quality SGP40 v%s" % __version__)

# create module object for xbee
module=sensorlab.Module()
time.sleep(2) # wait for config to be applied
module.get_signal()

# create shutdown button and status led
button = sensorlab.Button(config.INPUT_BUTTON, module)
button.check(5000) # check for shutdown button
status_led = sensorlab.StatusLED(config.STATUS_LED)
status_led.off

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

# set up sensor
try:
    sgp40 = qwiic_sgp40.QwiicSGP40()
    if sgp40.begin() == False:
        pass
        # status_led.blink(20, 1.5)
        # module.reset()
except Exception as e:
    print(e)

# initialize comms failure count
drm_fail = mqtt_fail = http_fail = 0

# first sample immediately
t1 = time.ticks_add(time.ticks_ms(), int(config.UPLOAD_RATE * -1000))
# main loop
while True:
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.UPLOAD_RATE * 1000: # time for a sample
        t1 = time.ticks_ms()
        try:
            air_quality_index = sgp40.get_VOC_index()
        except Exception as e:
            print(e)
            status_led.blink(4, 1.5)
        if config.HTTP_UPLOAD:
            try:
                json = {"variable":config.HTTP_VARIABLE,"value":air_quality_index,"unit":config.HTTP_UNIT}
                response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
                print(" http -> " , air_quality_index," (" + str(response.status_code), response.reason.decode(), 
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
                client.publish(config.MQTT_TOPIC, str(air_quality_index))
                print(" mqtt -> ", air_quality_index)
                mqtt_fail = 0
            except Exception as e:
                print(e)
                mqtt_fail += 1
                status_led.blink(2, 0.2)
        if config.DRM_UPLOAD:
            try:
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM,air_quality_index)
                data.send(timeout=10)
                print(" drm -> ", air_quality_index)
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
