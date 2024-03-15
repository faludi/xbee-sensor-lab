To avoid a memory error on XBee, compile the DFRobot_SGP40_VOCAlgorithm.py module from the downloaded package into a .mpy file using mpy-cross. The version for MicroPython 1.18 is https://pypi.org/project/mpy-cross/1.18/

Here is the terminal command to compile it:

mpy-cross -mno-unicode -msmall-int-bits=31 DFRobot_SGP40_VOCAlgorithm.py