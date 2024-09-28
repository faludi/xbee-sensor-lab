# configuration file for xbee sensor lab Joystick

__version__ = "1.3.0"

from digi import cloud

UPLOAD_RATE = 2 # upload frequency in seconds
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = True
if MQTT_UPLOAD:
    MQTT_TOPIC1 = "joystick/xaxis"
    MQTT_TOPIC2 = "joystick/yaxis"
    MQTT_TOPIC3 = "joystick/button"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE1 = "x-axis"
    HTTP_VARIABLE2 = "y-axis"
    HTTP_VARIABLE3 = "button"
    HTTP_UNIT1 = ""
    HTTP_UNIT2 = ""
    HTTP_UNIT3 = ""

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/joystick/x-axis"
    STREAM2 = "xbsl/joystick/y-axis"
    STREAM3 = "xbsl/joystick/button"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP