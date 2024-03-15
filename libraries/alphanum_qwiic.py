
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


import time

DEFAULT_ADDRESS = 0x70  # default i2c address

class ALPHANUM_QWIIC():

    # Define constants for segment bits
    SEG_A = 0x0001
    SEG_B = 0x0002
    SEG_C = 0x0004
    SEG_D = 0x0008
    SEG_E = 0x0010
    SEG_F = 0x0020
    SEG_G = 0x0040
    SEG_H = 0x0080
    SEG_I = 0x0100
    SEG_J = 0x0200
    SEG_K = 0x0400
    SEG_L = 0x0800
    SEG_M = 0x1000
    SEG_N = 0x2000

    # Blink rate
    ALPHA_BLINK_RATE_NOBLINK = 0b00
    ALPHA_BLINK_RATE_2HZ = 0b01
    ALPHA_BLINK_RATE_1HZ = 0b10
    ALPHA_BLINK_RATE_0_5HZ = 0b11

    # Display settings
    ALPHA_DISPLAY_ON = 0b1
    ALPHA_DISPLAY_OFF = 0b0

    # Decimal settings
    ALPHA_DECIMAL_ON = 0b1
    ALPHA_DECIMAL_OFF = 0b0

    # Colon settings
    ALPHA_COLON_ON = 0b1
    ALPHA_COLON_OFF = 0b0

    # Commands
    ALPHA_CMD_SYSTEM_SETUP = 0b00100000
    ALPHA_CMD_DISPLAY_SETUP = 0b10000000
    ALPHA_CMD_DIMMING_SETUP = 0b11100000

    SFE_ALPHANUM_UNKNOWN_CHAR = 95

    # Lookup table of segments for various characters
    alphanumeric_segs = []
    # nmlkjihgfedcba  0b00000011100011 = degree symbol?
    alphanumeric_segs.append(0b00000000000000)  # ' ' (space)
    alphanumeric_segs.append(0b00001000001000)  # '!'
    alphanumeric_segs.append(0b00001000000010)  # '"'
    alphanumeric_segs.append(0b01001101001110)  # '#'
    alphanumeric_segs.append(0b01001101101101)  # '$'
    alphanumeric_segs.append(0b10010000100100)  # '%'
    alphanumeric_segs.append(0b00110011011001)  # '&'
    alphanumeric_segs.append(0b00001000000000)  # '''
    alphanumeric_segs.append(0b00000000111001)  # '('
    alphanumeric_segs.append(0b00000000001111)  # ')'
    alphanumeric_segs.append(0b11111010000000)  # '*'
    alphanumeric_segs.append(0b01001101000000)  # '+'
    alphanumeric_segs.append(0b10000000000000)  # ','
    alphanumeric_segs.append(0b00000101000000)  # '-'
    alphanumeric_segs.append(0b01000000000000)  # '.'
    alphanumeric_segs.append(0b10010000000000)  # '/'
    alphanumeric_segs.append(0b00000000111111)  # '0'
    alphanumeric_segs.append(0b00010000000110)  # '1'
    alphanumeric_segs.append(0b00000101011011)  # '2'
    alphanumeric_segs.append(0b00000101001111)  # '3'
    alphanumeric_segs.append(0b00000101100110)  # '4'
    alphanumeric_segs.append(0b00000101101101)  # '5'
    alphanumeric_segs.append(0b00000101111101)  # '6'
    alphanumeric_segs.append(0b01010000000001)  # '7'
    alphanumeric_segs.append(0b00000101111111)  # '8'
    alphanumeric_segs.append(0b00000101100111)  # '9'
    alphanumeric_segs.append(0b01001000000000)  # ':'
    alphanumeric_segs.append(0b10001000000000)  # ';'
    alphanumeric_segs.append(0b00110000000000)  # '<'
    alphanumeric_segs.append(0b00000101001000)  # '='
    alphanumeric_segs.append(0b01000010000000)  # '>'
    alphanumeric_segs.append(0b01000100000011)  # '?'
    alphanumeric_segs.append(0b00001100111011)  # '@'
    alphanumeric_segs.append(0b00000101110111)  # 'A'
    alphanumeric_segs.append(0b01001100001111)  # 'B'
    alphanumeric_segs.append(0b00000000111001)  # 'C'
    alphanumeric_segs.append(0b01001000001111)  # 'D'
    alphanumeric_segs.append(0b00000101111001)  # 'E'
    alphanumeric_segs.append(0b00000101110001)  # 'F'
    alphanumeric_segs.append(0b00000100111101)  # 'G'
    alphanumeric_segs.append(0b00000101110110)  # 'H'
    alphanumeric_segs.append(0b01001000001001)  # 'I'
    alphanumeric_segs.append(0b00000000011110)  # 'J'
    alphanumeric_segs.append(0b00110001110000)  # 'K'
    alphanumeric_segs.append(0b00000000111000)  # 'L'
    alphanumeric_segs.append(0b00010010110110)  # 'M'
    alphanumeric_segs.append(0b00100010110110)  # 'N'
    alphanumeric_segs.append(0b00000000111111)  # 'O'
    alphanumeric_segs.append(0b00000101110011)  # 'P'
    alphanumeric_segs.append(0b00100000111111)  # 'Q'
    alphanumeric_segs.append(0b00100101110011)  # 'R'
    alphanumeric_segs.append(0b00000110001101)  # 'S'
    alphanumeric_segs.append(0b01001000000001)  # 'T'
    alphanumeric_segs.append(0b00000000111110)  # 'U'
    alphanumeric_segs.append(0b10010000110000)  # 'V'
    alphanumeric_segs.append(0b10100000110110)  # 'W'
    alphanumeric_segs.append(0b10110010000000)  # 'X'
    alphanumeric_segs.append(0b01010010000000)  # 'Y'
    alphanumeric_segs.append(0b10010000001001)  # 'Z'
    alphanumeric_segs.append(0b00000000111001)  # '['
    alphanumeric_segs.append(0b00100010000000)  # '\'
    alphanumeric_segs.append(0b00000000001111)  # ']'
    alphanumeric_segs.append(0b10100000000000)  # '^'
    alphanumeric_segs.append(0b00000000001000)  # '_'
    alphanumeric_segs.append(0b00000010000000)  # '`'
    alphanumeric_segs.append(0b00000101011111)  # 'a'
    alphanumeric_segs.append(0b00100001111000)  # 'b'
    alphanumeric_segs.append(0b00000101011000)  # 'c'
    alphanumeric_segs.append(0b10000100001110)  # 'd'
    alphanumeric_segs.append(0b00000001111001)  # 'e'
    alphanumeric_segs.append(0b00000001110001)  # 'f'
    alphanumeric_segs.append(0b00000110001111)  # 'g'
    alphanumeric_segs.append(0b00000101110100)  # 'h'
    alphanumeric_segs.append(0b01000000000000)  # 'i'
    alphanumeric_segs.append(0b00000000001110)  # 'j'
    alphanumeric_segs.append(0b01111000000000)  # 'k'
    alphanumeric_segs.append(0b01001000000000)  # 'l'
    alphanumeric_segs.append(0b01000101010100)  # 'm'
    alphanumeric_segs.append(0b00100001010000)  # 'n'
    alphanumeric_segs.append(0b00000101011100)  # 'o'
    alphanumeric_segs.append(0b00010001110001)  # 'p'
    alphanumeric_segs.append(0b00100101100011)  # 'q'
    alphanumeric_segs.append(0b00000001010000)  # 'r'
    alphanumeric_segs.append(0b00000110001101)  # 's'
    alphanumeric_segs.append(0b00000001111000)  # 't'
    alphanumeric_segs.append(0b00000000011100)  # 'u'
    alphanumeric_segs.append(0b10000000010000)  # 'v'
    alphanumeric_segs.append(0b10100000010100)  # 'w'
    alphanumeric_segs.append(0b10110010000000)  # 'x'
    alphanumeric_segs.append(0b00001100001110)  # 'y'
    alphanumeric_segs.append(0b10010000001001)  # 'z'
    alphanumeric_segs.append(0b10000011001001)  # '{'
    alphanumeric_segs.append(0b01001000000000)  # '|'
    alphanumeric_segs.append(0b00110100001001)  # '}'
    alphanumeric_segs.append(0b00000101010010)  # '~'
    alphanumeric_segs.append(0b11111111111111)  # Unknown character (DEL or RUBOUT)

    display_on_off = 0  # Tracks the on/off state of the display
    decimal_on_off = 0  # Tracks the on/off state of the decimal segment
    colon_on_off = 0    # Tracks the on/off state of the colon segment
    blink_rate = ALPHA_BLINK_RATE_NOBLINK   # Tracks the current blinking status
    digit_position = 0  # Tracks the position of the current digit

    display_RAM = [0] * 16
    display_content = [0] * (4 + 1)


    def __init__(self, i2c, address=DEFAULT_ADDRESS):
        self._i2c = i2c
        self.address=address
        self.initialize()

    def is_connected(self):
        return  self.address in self._i2c.scan()
    
    def initialize(self):
        self.enable_system_clock()
        self.set_brightness(15)
        self.set_blink_rate(self.ALPHA_BLINK_RATE_NOBLINK)
        self.set_display(True)
        self.clear()


    
    def enable_system_clock(self):
        buff = bytearray([self.ALPHA_CMD_SYSTEM_SETUP |1])
        status = self._i2c.writeto(self.address, buff)
        time.sleep(0.001)   # Allow display to start
        return status
    
    def set_brightness(self, duty):
        # duty must be between 0 and 15
        clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
        duty = clamp(duty, 0, 15)
        buff = bytearray([self.ALPHA_CMD_DIMMING_SETUP | duty])
        status = self._i2c.writeto(self.address, buff)
        return status
    
    def set_blink(self, rate):
        # frequency can be 2.0, 1.0, 0.5, or 0 Hz
        self.display_on_off = True
        if rate == 2.0:
            self.blink_rate = self.ALPHA_BLINK_RATE_2HZ
        elif rate == 1.0:
            self.blink_rate = self.ALPHA_BLINK_RATE_1HZ
        elif rate == 0.5:
            self.blink_rate = self.ALPHA_BLINK_RATE_0_5HZ
        else:
            self.blink_rate = self.ALPHA_BLINK_RATE_NOBLINK # default is no blink
        buff = bytearray([self.ALPHA_CMD_DISPLAY_SETUP | (self.blink_rate << 1) | self.display_on_off])
        status = self._i2c.writeto(self.address, buff)
        return status
    
    def set_display(self, turn_on_display=True):
        if turn_on_display:
            self.display_on_off = self.ALPHA_DISPLAY_ON
        else:
            self.display_on_off = self.ALPHA_DISPLAY_OFF     
        buff = bytearray([self.ALPHA_CMD_DISPLAY_SETUP | (self.blink_rate << 1) | self.display_on_off])
        status = self._i2c.writeto(self.address, buff)
        return status
    
    def clear(self):
        self.display_RAM = [0] * 16
        return self.update_display()

    def set_decimal(self, turn_on_decimal, update=True):
        adr = 0x03
        if turn_on_decimal:
            self.decimal_on_off = self.ALPHA_DECIMAL_ON
            dat = 0x01
            self.display_RAM[adr] = self.display_RAM[adr] | dat
        else:
            self.decimal_on_off = self.ALPHA_DECIMAL_OFF
            dat = 0x00
            self.display_RAM[adr] = self.display_RAM[adr] & dat
        if update:
            return self.update_display()
    
    def set_colon(self, turn_on_colon, update=True):
        adr = 0x01
        if turn_on_colon:
            self.decimal_on_off = self.ALPHA_COLON_ON
            dat = 0x01
            self.display_RAM[adr] = self.display_RAM[adr] | dat
        else:
            self.decimal_on_off = self.ALPHA_COLON_OFF
            dat = 0x00
            self.display_RAM[adr] = self.display_RAM[adr] & dat
        if update:
            return self.update_display()

    def illuminate_segment(self, segment, position):
        # lights up a specific segment of the display, A-N in the position of the digit
        segment = ord(segment)
        com = segment - ord('A') # Convert the segment letter back to a number
        
        if com > 6:
            com = com - 7
        # Special cases in which the segment order is a lil switched.
        if segment == ord('I'):
            com = 0
        if segment == ord('H'):
            com = 1
        
        if segment > ord('G'):
            position = position + 4
        
        adr = com * 2

        # Determine the address
        if position > 7:
            adr = adr + 1

        # Determine the data bit
        if position > 7:
            position = position - 8

        dat = 1 << position

        self.display_RAM[adr] = self.display_RAM[adr] | dat

   
    # Given a binary set of segments and a digit, store this data into the RAM array
    def illuminate_char(self, segments_to_turn_on, position):
        # Given a binary set of segments and a digit, store this data into the RAM array
        clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
        position = clamp(position, 0, 3)
        for i in range(0, 14):
            if (segments_to_turn_on >> i) & 0b1:
                temp_char = ord('A') + i
                temp_char = chr(temp_char)
                self.illuminate_segment(temp_char, position) # Convert the segment number to a letter
    


    def print_char(self, display_char, position):
    # Print a character, for a given position, on display
        # Convert character to ASCII representation
        display_char = ord(display_char)
        character_position = 65532

        # Space
        if display_char == ord(' '):
            character_position = 0
        # Printable symbols -- between first character '!' and last character '~'
        elif display_char >= ord('!') and display_char <= ord('~'):
            character_position = display_char - ord('!') + 1

        # Take care of special characters by turning correct segment on 
        # if character_position == 14:    # '.'
        #     self.set_decimal(True, update=False)
        # if character_position == 26:    # ':'
        #     self.set_colon(True, update=False)
        if character_position == 65532: # unknown character
            character_position = self.SFE_ALPHANUM_UNKNOWN_CHAR

        self.illuminate_char(self.alphanumeric_segs[character_position], position)
    

    # ---------------------------------------------------------------------------------
    # print(print_string)
    #
   
    def print(self, print_string):
         # Print a whole string to the alphanumeric display(s)
        self.clear()
        
        self.digit_position = 0

        for i in range(0, len(print_string)):
            # # For special characters like '.' or ':', do not increment the digit position
            # if print_string[i] == '.':
            #     self.print_char('.', 0)
            # elif print_string[i] == ':':
            #     self.print_char(':', 0)
            # else:
            self.print_char(print_string[i], self.digit_position)
            # Record to internal list
            self.display_content[i] = print_string[i]

            self.digit_position = self.digit_position + 1
            self.digit_position = self.digit_position % 4
        
        self.update_display()

    def print_scroll(self, print_string, delay=0.6, speed=0.3):
        # strip out decimal and colon so they don't trigger special segments
        # does it make more sense for those to be written explicitly-only throughout?
        # print_string = print_string.replace(':', '')
        # print_string = print_string.replace('.', '')
        str_len = len(print_string)
        if str_len <=4:
            self.print(print_string)
        else:
            self.print(print_string[:4])
            time.sleep(delay)
            for item in range(1,str_len-3):
                self.print(print_string[item:item+4])
                time.sleep(speed)
            #self.print(print_string[len-print_string % 4 ])



    def update(self):
        # Push the contents of display_RAM out to the device
        status = True
        buff = bytearray(self.display_RAM)
        status = self._i2c.writeto_mem(self.address, 0, buff)
        return status

    update_display = update
    set_blink_rate = set_blink
