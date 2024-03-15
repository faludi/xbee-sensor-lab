# configuration file for xbee sensor lab SMS Text display

__version__ = "1.2.0"

from digi import cloud

STREAM1 = "xbsl/sms/text"
STREAM2 = "xbsl/sms/sender"
STREAM3 = "xbsl/sms/phone_number"
REFRESH_RATE = 1800 # delay in seconds before reverting to phone number display
UPPERCASE = True # sets whether alphanumeric display is all uppercase or mixed case
USE_HTTP = False # sets whether to use an authenticated HTTP API upload for long messages
DEFAULT_STREAM_PREFIX = '00010000-00000000-03559465-20053518/'
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 5 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
