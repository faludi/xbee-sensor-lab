# configuration file for xbee sensor lab BLE Scanner

__version__ = "1.3.0"

from digi import cloud


FREQ = 400000
UPLOAD_RATE = 15 # upload frequency in seconds
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = False
if MQTT_UPLOAD:
    MQTT_TOPIC1 = "ble_scanner/distance"
    MQTT_TOPIC2 = "ble_scanner/meters"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE1 = "distance"
    HTTP_VARIABLE1 = "meters"
    HTTP_UNIT1 = ""
    HTTP_UNIT1 = "m"

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/ble_scanner/distance"
    STREAM2 = "xbsl/ble_scanner/meters"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
