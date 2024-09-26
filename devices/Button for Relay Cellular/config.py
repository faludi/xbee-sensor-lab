# configuration file for xbee sensor lab Button Qwiic

__version__ = "1.3.0"

from digi import cloud

RELAY_CHECK_RATE = 900 # relay check rate in seconds (900 == 15 minutes)
TARGET_ID = "00010000-00000000-03559465-20042586" # the Digi Remote Manager ID of the Relay device
MAX_COMMS_FAIL = 10 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = True
if MQTT_UPLOAD:
    MQTT_TOPIC = "button"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE = "button"
    HTTP_UNIT = ""

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/button"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP