# Sensor Lab - SMS Text Display

# !!! IF USING HTTP, ADD AUTHENTICATION INFO TO THE secrets_template.py FILE AND RENAME IT TO BE secrets.py  !!!

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
import network
import xbee
import alphanum_qwiic
from machine import I2C
import uio
from digi import cloud

# there is currently a 93-character limit in the datastream upload module,
#  therefore an authenticated API call via HTTP can be selected in the config file
if config.USE_HTTP:
    from remotemanager import RemoteManagerConnection
    import secrets

__version__ = "1.2.3"
print(" Digi Sensor Lab - SMS Text Display v%s" % __version__)

# defines a function for uploading data when using HTTP API calls
if config.USE_HTTP:
    def upload_datapoint(stream_id, data):
        try:
            response = rm.add_datapoint(stream_id, data)
            return response is not None
        except OSError:
            return False
        
    # Create the connection with Digi Remote Manager.
    credentials = {'username': secrets.DRM_USER, 'password': secrets.DRM_PASS}
    rm = RemoteManagerConnection(credentials=credentials)
    try:
        imei = xbee.atcmd("IM")
        stream_prefix = '00010000-00000000-0' + imei[0:7] + '-' + imei [7:15] + '/'
        print('stream_prefix')
    except Exception as e:
        print(e)
        stream_prefix = config.DEFAULT_STREAM_PREFIX
    print('stream_prefix:', stream_prefix)

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

# allows receipt of SMS
cellular = network.Cellular()

# set up display
try:
    i2c = I2C(1, freq=400000)
    display=alphanum_qwiic.ALPHANUM_QWIIC(i2c)
except OSError as e:
    print(' display not found error:', e)
    status_led.blink(20, 1.5)
    module.reset()

# format current phone number and send to DRM
ph = xbee.atcmd("PH")
phone_number = ph
if len(ph) == 11:
    phone_number = ph[0] + "-" + ph[1:4] + "-" + ph[4:7] + "-" + ph[7:11]
print('phone number:', phone_number)
message = 'TEXT ME AT ' + phone_number
for i in range(2): # try the upload twice as the first one often fails
    try: 
        data = cloud.DataPoints(config.DRM_TRANSPORT)
        data.add(config.STREAM1,message)
        data.send(timeout=10)
        data = cloud.DataPoints(config.DRM_TRANSPORT)
        data.add(config.STREAM3,ph)
        data.send(timeout=10)
        print(" drm -> ", ph)
    except Exception as e:
        print(e)

# initialize comms failure count
drm_fail = 0

print('waiting for messages...')
# main loop
t1 = time.ticks_ms()
recent_messages = False
while True:
    t2 = time.ticks_ms() # mark the current time
    # Check if the XBee has received any SMS.
    sms = cellular.sms_receive()
    if sms != None:
        t1 = time.ticks_ms() # mark the time of message arrival
        recent_messages = True
        message = sms['message']
        sender = sms['sender']
        print("SMS received from %s >> %s" % (sender, message))
        file = uio.open("log.txt", mode="a")
        # (2023, 7, 10, 17, 50, 0, 0, 191)
        # 2005-03-19 15:10:26,618
        now = time.localtime()
        date_str = str(now[0]) + '-' + "{:02d}".format(now[1]) + '-' + "{:02d}".format(now[2])
        time_str = "{:02d}".format(now[3]) + ':' +  "{:02d}".format(now[4]) + ':' +  "{:02d}".format(now[5])
        file.write(date_str + ' ' + time_str + ' ' + sender + " " + message + '\n')
        if file.tell() > 100000:  # clear log file if it gets larger than 100K, for safety
            uio.open("log.txt", mode="w")
            file.write(sender + " " + message + '\n')
        file.close()
        try: 
            if len(message) > 128: # if the message is a long one...
                if config.USE_HTTP: # either upload entire text using HTTP API...
                    try: 
                        upload_datapoint(stream_prefix + config.STREAM1, message)
                    except Exception as e:
                        print(e)
                        drm_fail += 1
                else: # or break long texts into chunks for upload with digi.cloud data streams
                    chunk_size = 92
                    chunks = [message[i:i+chunk_size] for i in range(0, len(message), chunk_size)]
                    for chunk in chunks:
                        data = cloud.DataPoints(config.DRM_TRANSPORT)
                        data.add(config.STREAM1,chunk)
                        data.send(timeout=10)
            else: # short messages can always be uploaded without HTTP API
                data = cloud.DataPoints(config.DRM_TRANSPORT)
                data.add(config.STREAM1,message)
                data.send(timeout=10)
            data = cloud.DataPoints(config.DRM_TRANSPORT)
            data.add(config.STREAM2,sender)
            data.send(timeout=10)
            print(" drm -> ", message, sender)
            drm_fail = 0
        except Exception as e:
            print(e)
            drm_fail += 1
            status_led.blink(2, 0.2)
    if config.UPPERCASE == True: # uppercase all text if so configured
        message = message.upper()
    if 'display' in locals(): # check if display has been defined
        try:
            display.print_scroll(message, 0.6, 0.3)
            time.sleep(1.5)
            display.clear()
            time.sleep(1)
        except OSError as e:
            print('display not found error:', e)
            status_led.blink(4, 1.5)

    # Even if sleep time changes, at minimum 100 ms before checking for data again.
    time.sleep(0.1)

    # if refresh time has passed or system has been idle for 24 hours, set "Text Me" message
    if ((time.ticks_diff(t2, t1) >= config.REFRESH_RATE * 1000) and recent_messages == True) or (time.ticks_diff(t2, t1) >= 86400 * 1000): # revert to phone number display
        recent_messages = False
        t1 = time.ticks_ms() # mark the refresh time
        message = 'TEXT ME AT ' + phone_number
        data = cloud.DataPoints(config.DRM_TRANSPORT)
        data.add(config.STREAM1,message)
        data.send(timeout=10)

    button.check(5000) # check for shutdown button
    if drm_fail >= config.MAX_COMMS_FAIL:
        print (" drm_fails {drm}".format(drm=drm_fail))
        module.reset()
    dog.feed() # update watchdog timer


