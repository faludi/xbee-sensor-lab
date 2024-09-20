# configuration file for xbee sensor lab GNSS

__version__ = "1.3.0"

from digi import cloud

UPLOAD_RATE = 60 # upload frequency in seconds
MAX_COMMS_FAIL = 10 # number of consecutive communications failures before reset
LAT_LONG_FILE = "latlong.txt" # file for storing cached GNSS readings
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages

MQTT_UPLOAD = False
if MQTT_UPLOAD:
    MQTT_TOPIC1 = "GNSS/latitude"
    MQTT_TOPIC2 = "GNSS/longitude"
    MQTT_TOPIC3 = "GNSS/cached"
    MQTT_TOPIC4 = "GNSS/position"
    MQTT_SERVER = "mqtt.tago.io"
    MQTT_PORT = 8883
    MQTT_SSL = True
    MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
if HTTP_UPLOAD:
    import secrets
    HTTP_URL = "http://api.tago.io/data"
    HTTP_HEADERS = {"Device-Token": secrets.HTTP_TOKEN}
    HTTP_VARIABLE1 = "latitude"
    HTTP_VARIABLE2 = "longitude"
    HTTP_VARIABLE3 = "cached"
    HTTP_VARIABLE4 = "position"
    HTTP_UNIT1 = "deg"
    HTTP_UNIT2 = "deg"
    HTTP_UNIT3 = ""
    HTTP_UNIT4 = ""

DRM_UPLOAD = True
if DRM_UPLOAD:
    STREAM1 = "xbsl/GNSS/latitude"
    STREAM2 = "xbsl/GNSS/longitude" 
    STREAM3 = "xbsl/GNSS/cached" # indicating live or cached result
    STREAM4 = "xbsl/GNSS/position" # compiles lat and long into a single value as "(<lat>,<long>)""
    DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP