# configuration file for xbee sensor lab person sensor

__version__ = "1.0.0"

from digi import cloud

STREAM1 = "xbsl/person_sensor/faces"
STREAM2 = "xbsl/person_sensor/attention"
UPLOAD_RATE = 5 # upload frequency in seconds
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
