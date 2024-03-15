
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


DEFAULT_ADDRESS = 0x38  # default i2c address for zio loudness sensor

GET_VALUE = [0x05] # register for loudness readings

class ZioLoudness():

  def __init__(self, i2c, addr=DEFAULT_ADDRESS):
    self.i2c = i2c
    self.addr=addr

  def get_loudness(self):
    buff=bytearray(GET_VALUE)
    self.i2c.writeto(self.addr, buff)
    buff2=bytearray(bytes(2))
    self.i2c.readfrom_into(self.addr, buff2)
    raw_value = (buff2[0] | (buff2[1] << 8))
    loudness = 20 + ((80 - 20) / (1023 - 0)) * (raw_value) # rough transform to dB
    return (loudness)
