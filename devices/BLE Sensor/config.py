# configuration file for xbee sensor lab BLE Sensor

__version__ = "1.2.1"

from digi import cloud

STREAM1 = "xbsl/ble_sensor/temperature"
STREAM2 = "xbsl/ble_sensor/humidity"
UPLOAD_RATE = 5 # upload frequency in seconds
AUTO_DISCOVERY = True # device will automatically discover and use the first Thunderboard that responds
SENSOR_ADDRESS_FILE = 'sensor_address.txt' # file where MAC address is stored. Manually edit this file if auto-discovery is off
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
MAX_BLE_FAIL = 10 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
