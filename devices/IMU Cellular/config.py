#  coniguration file for xbee sensor lab IMU

__version__ = "1.2.1"

from digi import cloud

STREAM1 = "xbsl/imu/ax"
STREAM2 = "xbsl/imu/ay"
STREAM3 = "xbsl/imu/az"
STREAM4 = "xbsl/imu/gx"
STREAM5 = "xbsl/imu/gy"
STREAM6 = "xbsl/imu/gz"
UPLOAD_RATE = 2 # upload frequency in seconds
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

