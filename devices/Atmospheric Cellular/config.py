# configuration file for xbee sensor lab Atmospheric

__version__ = "1.3.0"

from digi import cloud

UPLOAD_RATE = 2 # upload frequency in seconds
MAX_COMMS_FAIL = 15 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = True
if MQTT_UPLOAD:
    MQTT_TOPIC1 = "atmospheric/temperature"
    MQTT_TOPIC2 = "atmospheric/humidity"
    MQTT_TOPIC3 = "atmospheric/pressure"
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
    HTTP_VARIABLE3 = "pressure"
    HTTP_UNIT1 = "ºC"
    HTTP_UNIT2 = "% Rh"
    HTTP_UNIT3 = "kPa"

DRM_UPLOAD = False
if DRM_UPLOAD:
    STREAM1 = "xbsl/atmospheric/temperature"
    STREAM2 = "xbsl/atmospheric/humidity"
    STREAM3 = "xbsl/atmospheric/pressure"
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP
