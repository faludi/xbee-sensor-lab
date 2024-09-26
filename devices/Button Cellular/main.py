# Sensor Lab - Qwiic Button https://www.sparkfun.com/products/15932

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

"""
To turn LED on via the DRM API, edit this XML block to add your device ID, then POST to my.devicecloud.com/ws/sci
(You can also use the API Explorer under System on the DRM site.)

<sci_request version="1.0">
  <data_service>
    <targets>
      <device id="00000000-00000000-00000000-00000000"/>
    </targets>
    <requests>
      <device_request target_name="micropython">
        LED ON
      </device_request>
    </requests>
  </data_service>
</sci_request>

Commands in device_request can be:
LED ON
LED OFF
LED 128  #brigthness range from 0-255

"""

import sensorlab
import time
import config
import machine
import qwiic_button
import qwiic_i2c
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
print(" Digi Sensor Lab - Button v%s" % __version__)

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

# set up sensor and test LED
try:
    bus = qwiic_i2c.get_i2c_driver(freq=400000) # pass i2c driver to library to set custom frequency
    bt=qwiic_button.QwiicButton(i2c_driver = bus)
    if bt.begin() == False:
        status_led.blink(20, 1.5)
        module.reset()
    bt.LED_on(255)
    time.sleep(1)
    bt.LED_off()
except Exception as e:
    print(e)

# initialize comms failure count
drm_fail = mqtt_fail = http_fail = 0

# first sample immediately
t1 = t3 = time.ticks_add(time.ticks_ms(), int(config.UPLOAD_RATE * -1000))
last_press = -1
# main loop
while True:
    try:
        button_press = int(bt.is_button_pressed())
    except Exception as e:
        print(e)
        status_led.blink(4, 1.5)
    if last_press != button_press:
        last_press = button_press
        if config.HTTP_UPLOAD:
            try:
                json = {"variable":config.HTTP_VARIABLE,"value":button_press,"unit":config.HTTP_UNIT}
                response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
                print(" http -> " , button_press," (" + str(response.status_code), response.reason.decode(), 
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
                client.publish(config.MQTT_TOPIC, str(button_press))
                print(" mqtt -> ", button_press)
                mqtt_fail = 0
            except Exception as e:
                print(e)
                mqtt_fail += 1
                status_led.blink(2, 0.2)
        if config.DRM_UPLOAD:
            try: 
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM1,button_press)
                data.send(timeout=10)
                print(" drm -> ", button_press)
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
    time.sleep_ms(20)
    if max(drm_fail,mqtt_fail,http_fail) >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}, mqtt_fails {mqtt}, http_fails {http}".format(drm=drm_fail, mqtt=mqtt_fail, http=http_fail, ))
        module.reset()
    dog.feed() # update watchdog timer

    # check cloud for commands
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= 5 * 1000: # check DRM every 5 seconds
        t1 = time.ticks_ms()
    request = cloud.device_request_receive()
    if request is not None:
        # A device request has been received, process it.
        data = request.read()
        message = data.decode("utf-8").strip()
        if message == "LED ON":
            print(" LED on request received")
            bt.LED_on(255)
            written = request.write(bytes("LED IS ON", "utf-8"))
        elif message == "LED OFF":
            print(" LED off request received")
            bt.LED_off()
            written = request.write(bytes("LED IS OFF", "utf-8"))
        elif message.split()[0]=="LED" and message.split()[1].isdigit():
            brightness = int(message.split()[1])
            print(" LED brightness request received: ", brightness)
            bt.LED_on(brightness)
        else:
            written = request.write(bytes("UNKNOWN COMMAND", "utf-8"))
        request.close()

