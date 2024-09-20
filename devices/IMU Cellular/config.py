#  coniguration file for xbee sensor lab IMU

__version__ = "1.3.0"

from digi import cloud

UPLOAD_RATE = 2 # upload frequency in seconds
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = False
if MQTT_UPLOAD:
    MQTT_TOPIC = "imu"  # concatonate all variables into a single string
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE = "imu" # concatonate all variables into a single string
    HTTP_UNIT = ""

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/imu/ax" # separate uploads for each variable for DRM
    STREAM2 = "xbsl/imu/ay"
    STREAM3 = "xbsl/imu/az"
    STREAM4 = "xbsl/imu/gx"
    STREAM5 = "xbsl/imu/gy"
    STREAM6 = "xbsl/imu/gz"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP