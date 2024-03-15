
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

from machine import I2C, Pin
import network
import time
import xbee

__version__ = "1.2.0"

class Module:
    # xbee configuration performed automatically at each startup
    xbee_config = [
    ("MO", 7),
    ("N#", 2),
    ("BD", 7),
    ("AP", 4),
    ("D0", 3),
    ("D1", 6),
    ("P1", 6),
    ("WR","")
    ]

    # (ICCID_prefix, apn, carrier_profile)   carrier profiles: 1=None, 2=att, 3=verizon
    apns = [
    ("8901", "edneopate010.dpa", 2),
    ("8914", "digicpn.gw12.vzwentp", 3),
    ("89445", "hologram", 1),
    ("89357", "hologram",1 ) 
    ]

    def __init__(self):
        self.conn = network.Cellular()
        self.set_apn(Module.apns)
        for cmd,value in Module.xbee_config:
            xbee.atcmd(cmd, value)
            print(" " + cmd + "=" + str(value) )
        self.connect()

    def set_apn(self, apn_list):
        id=None
        print(" waiting for ICCID...") 
        count=0
        while True:
            id = xbee.atcmd("S#")
            if (id):
                break
            count = count + 1
            if count >= 15:
                count = 0
                print(".", end="")
            time.sleep(1)
        print(" ICCID:", id) 
        for prefix, apn, carrier_profile in apn_list:
            if id.startswith(prefix):
                xbee.atcmd("AN", apn)
                xbee.atcmd("CP", carrier_profile)
                print(" AN:", apn)
                print(" CP:", carrier_profile)

    def connect(self):
        print(" wait for cell network...")
        count=0
        while not self.conn.isconnected():
            time.sleep(2)
            count = count + 1
            if count >= 30:
                count = 0
                print(".", end="")
        print(" cell ok")

    def reset(self):
        print(" full reset...", end="")
        self.conn.shutdown(reset=True)

    def shutdown(self):
        self.conn.shutdown(reset=False)

    def get_signal(self):
        try:
            signal = self.conn.signal()
            for key, val in signal.items():
                print("", key.upper(), val)
            return signal
        except Exception as e:
            print(e)


class Button:
    def __init__(self, pin, module):
        self.pin = pin
        self.button = Pin(pin, Pin.IN, Pin.PULL_UP)
        self.module = module

    def check(self, press_time=5000):
        startTime = time.ticks_ms()
        while self.button.value() == 0:
            if time.ticks_ms() - startTime > press_time:
                print("shutting down cell module...")
                self.module.shutdown()
                print("shutdown complete")
                raise SystemExit(0)
            
class StatusLED:
    def __init__(self, pin):
        self.pin = pin
        self.status_led = Pin(pin, Pin.OUT)
        self.status_led.off()

    def blink(self, cycles=1, delay=1):
        for cycle in range(cycles):
            self.status_led.on()
            time.sleep(delay/2)
            self.status_led.off()
            time.sleep(delay/2)
    
    def on(self):
        self.status_led.on()

    def off(self):
        self.status_led.off()
