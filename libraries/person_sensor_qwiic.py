
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

Based on manufacturers sample code: https://github.com/usefulsensors/person_sensor_circuit_python
'''

import struct

__version__ = "1.0.1"

PERSON_SENSOR_I2C_ADDRESS = 0x62  # default i2c address for person sensor

# # i2c commands not currently in use
# PERSON_SENSOR_REG_MODE = 0x01
# PERSON_SENSOR_REG_ENABLE_ID = 0x02
# PERSON_SENSOR_REG_SINGLE_SHOT = 0x03
# PERSON_SENSOR_REG_CALIBRATE_ID = 0x04
# PERSON_SENSOR_REG_PERSIST_IDS = 0x05
# PERSON_SENSOR_REG_ERASE_IDS = 0x06
# PERSON_SENSOR_REG_DEBUG_MODE = 0x07

PERSON_SENSOR_I2C_HEADER_FORMAT = "BBH"
PERSON_SENSOR_I2C_HEADER_BYTE_COUNT = struct.calcsize(
    PERSON_SENSOR_I2C_HEADER_FORMAT)

PERSON_SENSOR_FACE_FORMAT = "BBBBBBbB"
PERSON_SENSOR_FACE_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_FACE_FORMAT)

PERSON_SENSOR_FACE_MAX = 4
PERSON_SENSOR_RESULT_FORMAT = PERSON_SENSOR_I2C_HEADER_FORMAT + \
    "B" + PERSON_SENSOR_FACE_FORMAT * PERSON_SENSOR_FACE_MAX + "H"
PERSON_SENSOR_RESULT_BYTE_COUNT = struct.calcsize(PERSON_SENSOR_RESULT_FORMAT)

class person_sensor():

  def __init__(self, i2c, addr=PERSON_SENSOR_I2C_ADDRESS):
    self.i2c = i2c
    self.addr=addr

  def num_faces(self):
     num_faces, faces = self.get_data()
     return num_faces
  
  def face_data(self):
    num_faces, faces = self.get_data()
    return faces
 
  def get_data(self):
    read_data = bytearray(PERSON_SENSOR_RESULT_BYTE_COUNT)
    self.i2c.readfrom_into(PERSON_SENSOR_I2C_ADDRESS, read_data)
    offset = 0
    (pad1, pad2, payload_bytes) = struct.unpack_from(
        PERSON_SENSOR_I2C_HEADER_FORMAT, read_data, offset)
    offset = offset + PERSON_SENSOR_I2C_HEADER_BYTE_COUNT

    (num_faces) = struct.unpack_from("B", read_data, offset)
    num_faces = int(num_faces[0])
    offset = offset + 1

    faces = []
    for i in range(num_faces):
        (box_confidence, box_left, box_top, box_right, box_bottom, id_confidence, id,
          is_facing) = struct.unpack_from(PERSON_SENSOR_FACE_FORMAT, read_data, offset)
        offset = offset + PERSON_SENSOR_FACE_BYTE_COUNT
        face = {
            "box_confidence": box_confidence,
            "box_left": box_left,
            "box_top": box_top,
            "box_right": box_right,
            "box_bottom": box_bottom,
            "id_confidence": id_confidence,
            "id": id,
            "is_facing": is_facing,
        }
        faces.append(face)

    # print('debug: num faces:', num_faces, faces)

    # returns an integer for number of faces detected, and an array with data for each face
    return(num_faces, faces) 
