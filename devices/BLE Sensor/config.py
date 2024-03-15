# configuration file for xbee sensor lab BLE Sensor

__version__ = "1.2.0"

from digi import cloud

STREAM1 = "xbsl/ble_sensor/temperature"
STREAM2 = "xbsl/ble_sensor/humidity"
FREQ = 400000
UPLOAD_RATE = 5 # upload frequency in seconds
THUNDERBOARD_ADDRESS =  '0C:43:14:F4:61:A1'
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
