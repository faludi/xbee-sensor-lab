# configuration file for xbee sensor lab Atmospheric

__version__ = "1.2.0"

from digi import cloud

STREAM1 = "xbsl/atmospheric/temperature"
STREAM2 = "xbsl/atmospheric/humidity"
STREAM3 = "xbsl/atmospheric/pressure"
UPLOAD_RATE = 2 # upload frequency in seconds
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
