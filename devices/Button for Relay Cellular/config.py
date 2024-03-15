# configuration file for xbee sensor lab Button Qwiic

__version__ = "1.2.1"

from digi import cloud

STREAM1 = "xbsl/button"
RELAY_CHECK_RATE = 900 # relay check rate in seconds (900 == 15 minutes)
TARGET_ID = "00010000-00000000-03559465-20042586" # the Digi Remote Manager ID of the Relay device
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 10 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
