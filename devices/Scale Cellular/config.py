# configuration file for xbee sensor lab Scale

__version__ = "1.3.0"

from digi import cloud


UPLOAD_RATE = 2 # upload frequency in seconds
ZERO_OFFSET = 67120  # initial calibration, hold D0 button on boot to update
CALIBRATION_FACTOR = 250 # initial calibration, hold D0 button on boot to update
CALIBRATION_FILE = 'calibration.txt'
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = True
if MQTT_UPLOAD:
    MQTT_TOPIC = "scale"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE = "scale"
    HTTP_UNIT = "grams"

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM = "xbsl/scale"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP