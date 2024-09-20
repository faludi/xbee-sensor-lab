# Sensor Lab - Qwiic Button for Relay https://www.sparkfun.com/products/15932

# !!! ADD AUTHENTICATION INFO TO THE secrets_template.py FILE AND RENAME IT TO BE secrets.py  !!!

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
import secrets  
import time
import config
import machine
import qwiic_button
import urequests
from remotemanager import RemoteManagerConnection
import qwiic_i2c
if config.DRM_UPLOAD:
    from digi import cloud
if config.MQTT_UPLOAD:
    from umqtt.simple import MQTTClient
    import secrets
if config.HTTP_UPLOAD:
    import urequests

__version__ = "1.3.0"
print(" Digi Sensor Lab - Button for Relay v%s" % __version__)

# commands to exchange with Remote Manager
RELAY_ON = 'RELAY ON'
RELAY_ON_SUCCESS = 'RELAY IS ON'
RELAY_OFF = 'RELAY OFF'
RELAY_OFF_SUCCESS = 'RELAY IS OFF'
RELAY_STATE = 'RELAY STATE'
DEVICE_NOT_CONNECTED = 'Device Not Connected'
STREAMS_URI = 'https://remotemanager.digi.com/ws/sci'

# extends class to include uploading messages
class RemoteManagerConnection(RemoteManagerConnection):
    def upload_sci_message(self, data, headers=None):
        headers = self.set_headers(headers)
        response = urequests.post(STREAMS_URI, headers=headers, data=data)
        return (response)
    

# creates a relay controller that manages actuator state and all messaging
class RelayControl():
    
    def __init__(self, button, remote_manager):
        self.button = button
        self.remote_manager = remote_manager
    
    def set_relay(self, state):
        if state == True:
            print(" turning on relay")
            res = self.upload_message(config.TARGET_ID, RELAY_ON)
            status = self.process_response(res, RELAY_ON_SUCCESS, DEVICE_NOT_CONNECTED)
        else:
            print(" turning off relay")
            res = self.upload_message(config.TARGET_ID, RELAY_OFF)
            status = self.process_response(res, RELAY_OFF_SUCCESS, DEVICE_NOT_CONNECTED)
        return status
    
    def get_relay(self):
        res = self.upload_message(config.TARGET_ID, RELAY_STATE)
        status = self.process_state(res, RELAY_ON_SUCCESS, RELAY_OFF_SUCCESS, DEVICE_NOT_CONNECTED)
        if status is None:
            print(' state unknown')
        elif status is True:
            print(' relay confirmed on')
        else:
            print(' relay is confirmed off')
        return status

    def upload_message(self, target_id, target_message, target_name='micropython'):
        sci_request = """
            <sci_request version="1.0">
                            <data_service>
                                <targets>
                                <device id="{id}" />
                                </targets>
                            <requests>
                                <device_request target_name="{name}"> 
                                {message}
                                </device_request>
                            </requests>
                            </data_service>
                            </sci_request>
            """.format(id=target_id, name=target_name, message=target_message)
        
        try:
            response = self.remote_manager.upload_sci_message(sci_request)
            # print ("Response status_code: ", response.status_code)
            # print ("Response content: ", response.content)
            # print ("Response text: ", response.text)
            # print ("Response reason: ", response.reason)
            # print ("Response raw: ", response.raw)
            # print ("Response json: ", response.json())
            # print ("Response encoding: ", response.encoding)
            return response
        except OSError as e:
            print('Exception: ', e)
            return None


    def process_response(self, response, success, no_device):
        if response is not None:
            status_code = int(response.status_code)
            print (" status_code:", status_code)
            if not 200 <= status_code <= 299:
                print(' status outside 200-299 range')
                return False
            elif success in response.text:
                print(' success!')
                return True
            elif no_device in response.text:
                print(' remote device not connected')
                return False
            else:
                print(' unhandled respose: ', response.text)
                return False
        else:
            print(' no response')

    def process_state(self, response, on_message, off_message, no_device):
        if response is not None:
            status_code = int(response.status_code)
            print (" status_code:", status_code)
            if not 200 <= status_code <= 299:
                print(' status outside 200-299 range')
            elif on_message in response.text:
                print(' relay is on')
                return True
            elif off_message in response.text:
                print(' relay is off')
                return False
            elif no_device in response.text:
                print(' remote device not connected')
                return None
            else:
                print(' unhandled respose: ', response.text)
                return None
        else:
            print(' no response')


# create module object for xbee
module=sensorlab.Module()
time.sleep(2) # wait for config to be applied
module.get_signal()

# Create the connection with Digi Remote Manager.
credentials = {'username': secrets.DRM_USER, 'password': secrets.DRM_PASS}
rm = RemoteManagerConnection(credentials=credentials)
print(" target device:", config.TARGET_ID)

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

# set up sensor and test LED
try:
    bus = qwiic_i2c.get_i2c_driver(freq=400000) # pass i2c driver to library to set custom frequency
    bt=qwiic_button.QwiicButton(i2c_driver = bus)
    bt.LED_config(16, 2000, 2000)
    bt.set_debounce_time(1)
except Exception as e:
    print(e)
    status_led.blink(20, 1.5)
    module.reset()

# create button LED controller
relay_ctrl = RelayControl(bt, rm)

# initialize comms failure count
comm_fail  = 0

# start timer for relay checks
t1 = time.ticks_add(time.ticks_ms(), int(config.RELAY_CHECK_RATE * - 1000))
relay_state = False # state is unknown at this point
button_click = False

# main loop
while True:
    # periodically check relay state
    t2 = time.ticks_ms()
    if time.ticks_diff(t2, t1) >= config.RELAY_CHECK_RATE * 1000: # check relay state every 15 minutes
        t1 = time.ticks_ms() # update time for relay check
        print(' checking relay state...')
        state_check = relay_ctrl.get_relay()
        if state_check is not None:
            relay_state = state_check
        print(' relay check complete')
        print(' waiting for clicks...')

    if relay_state:
        bt.LED_on(255)
    else:
        bt.LED_off()
    try:
        if bt.has_button_been_clicked():
            button_click = True
            t1 = time.ticks_ms() # update time for relay check 
            print('clicked!')
            bt.clear_event_bits()
            if relay_state:
                bt.LED_config(12, 3000, 500)
            else:
                bt.LED_config(200, 3000, 0)
    except Exception as e:
        print(e)
        status_led.blink(4, 1.5)

    if button_click == True:
        if config.HTTP_UPLOAD:
            try:
                json = {"variable":config.HTTP_VARIABLE,"value":int(button_click),"unit":config.HTTP_UNIT}
                response = urequests.post(config.HTTP_URL, headers=config.HTTP_HEADERS, json=json, request_1_1=True)
                print(" http -> " , int(button_click)," (" + str(response.status_code), response.reason.decode(), 
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
                client.publish(config.MQTT_TOPIC, str(button_click))
                print(" mqtt -> ", int(button_click))
                comm_fail = 0
            except Exception as e:
                print(e)
                comm_fail += 1
                status_led.blink(2, 0.2)
        if config.DRM_UPLOAD:
            try: 
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM1,int(button_click))
                data.send(timeout=10)
                print(" drm -> ", int(button_click))
                comm_fail  = 0
            except Exception as e:
                print(e)
                comm_fail  += 1
                status_led.blink(2, 0.2)
        if relay_ctrl.set_relay(not relay_state): # toggle the relay and get results
            relay_state = not relay_state
        bt.clear_event_bits() # discard any intervening clicks
        button_click = False
        print(' waiting for clicks...')

    button.check(5000) # check for shutdown button
    time.sleep_ms(20)
    if comm_fail  >= config.MAX_COMMS_FAIL:
        print (" comm_fails {comm}".format(comm=comm_fail ))
        try:
            bt.LED_off()
        except:
            pass
        module.reset()
    dog.feed() # update watchdog timer


