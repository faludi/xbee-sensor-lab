# configuration file for xbee sensor lab SMS Text display

__version__ = "1.3.0"

from digi import cloud

REFRESH_RATE = 1800 # delay in seconds before reverting to phone number display
UPPERCASE = True # sets whether alphanumeric display is all uppercase or mixed case
USE_HTTP = False # sets whether to use an authenticated HTTP API upload for long messages
DEFAULT_STREAM_PREFIX = '00010000-00000000-03559465-20053518/'
MAX_COMMS_FAIL = 5 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = True
if MQTT_UPLOAD:
    MQTT_TOPIC1 = "sms/text"
    MQTT_TOPIC2 = "sms/sender"
    MQTT_TOPIC3 = "sms/phone_number"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE1 = "text"
    HTTP_VARIABLE2 = "sender"
    HTTP_VARIABLE3 = "phone_number"
    HTTP_UNIT1 = ""
    HTTP_UNIT2 = ""
    HTTP_UNIT3 = ""

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/sms/text"
    STREAM2 = "xbsl/sms/sender"
    STREAM3 = "xbsl/sms/phone_number"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP