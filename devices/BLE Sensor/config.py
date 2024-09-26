# configuration file for xbee sensor lab BLE Sensor

__version__ = "1.3.0"

from digi import cloud

UPLOAD_RATE = 5 # upload frequency in seconds
AUTO_DISCOVERY = True # device will automatically discover and use the first Thunderboard that responds
SENSOR_ADDRESS_FILE = 'sensor_address.txt' # file where MAC address is stored. Manually edit this file if auto-discovery is off
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
MAX_BLE_FAIL = 10 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = True
if MQTT_UPLOAD:
    MQTT_TOPIC1 = "ble_sensor/temperature"
    MQTT_TOPIC2 = "ble_sensor/humidity"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE1 = "temperature"
    HTTP_VARIABLE2 = "humidity"
    HTTP_UNIT1 = "ºC"
    HTTP_UNIT2 = "% Rh"

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/ble_sensor/temperature"
    STREAM2 = "xbsl/ble_sensor/humidity"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP