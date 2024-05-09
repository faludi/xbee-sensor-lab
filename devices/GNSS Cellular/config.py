# configuration file for xbee sensor lab GNSS

__version__ = "1.2.1"

from digi import cloud

STREAM1 = "xbsl/GNSS/latitude"
STREAM2 = "xbsl/GNSS/longitude" 
STREAM3 = "xbsl/GNSS/cached" # indicating live or cached result
STREAM4 = "xbsl/GNSS/position" # compiles lat and long into a single value as "(<lat>,<long>)""
UPLOAD_RATE = 60 # upload frequency in seconds
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 10 # number of consecutive communications failures before reset
LAT_LONG_FILE = "latlong.txt" # file for storing cached GNSS readings
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages