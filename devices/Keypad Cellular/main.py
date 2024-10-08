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
import qwiic_i2c
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
print(" Digi Sensor Lab - Keypad v%s" % __version__)

def mqtt_connect(client):
    print(" connecting to '%s'... " % config.MQTT_SERVER, end="")
    try:
        client.connect()
        print(" connected")
    except Exception as e:
        print(e)
        status_led.blink(10, 0.5)
        print(" mqtt connection failed")

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
    mqtt_connect(client)

#create watchdog timer
dog = machine.WDT(timeout=90000, response=machine.HARD_RESET)

# set up and test for sensor.
try:
    bus = qwiic_i2c.get_i2c_driver(freq=400000) # pass i2c driver to library to set custom frequency
    keypad = qwiic_keypad.QwiicKeypad(i2c_driver = bus)
    keypad.begin()
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# initialize comms failure count
drm_fail = mqtt_fail = http_fail = 0

# sending procedure functionalized for clarity
def send(value):
    global http_fail,mqtt_fail,drm_fail
    if config.HTTP_UPLOAD:
        try:
            json = {"variable":config.HTTP_VARIABLE,"value":value,"unit":config.HTTP_UNIT}
            response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
            print(" http -> " , value," (" + str(response.status_code), response.reason.decode(), 
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
            client.publish(config.MQTT_TOPIC, str(value))
            print(" mqtt -> ", value)
            mqtt_fail = 0
        except Exception as e:
            print(e)
            mqtt_fail += 1
            status_led.blink(2, 0.2)
    if config.DRM_UPLOAD:
        try:
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM,value)
            data.send(timeout=10)
            print(" drm -> ", value)
            drm_fail  = 0
        except Exception as e:
            print(e)
            drm_fail  += 1
            status_led.blink(2, 0.2)

# main loop
presses = ""
cnt = 0
active = False
t1 = t3 = time.ticks_ms() - (86400 * 1000)  # first upload immediately
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
        send(presses) # send as an integer
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
        send(-1) # send a negative one
    if config.MQTT_UPLOAD:
        if time.ticks_diff(t2, t3) >= 60 * 1000: # ping mqtt every 60 seconds
            t3 = time.ticks_ms()
            client.ping() # send a ping to the mqtt server
    button.check(5000) # check for shutdown button
    if max(drm_fail,mqtt_fail,http_fail) >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}, mqtt_fails {mqtt}, http_fails {http}".format(drm=drm_fail, mqtt=mqtt_fail, http=http_fail, ))
        module.reset()
    dog.feed() # update watchdog timer
