# configuration file for xbee sensor lab Loudness

__version__ = "1.3.1"

from digi import cloud
import secrets

MQTT_UPLOAD = False
MQTT_TOPIC = "loudness"
UPLOAD_RATE = 6 # upload frequency in seconds
MQTT_SERVER = "mqtt.tago.io"
MQTT_PORT = 8883
MQTT_SSL = True
MQTT_CLIENT_ID = "sensorlab_client_id"

HTTP_UPLOAD = False
HTTP_URL = "http://api.tago.io/data"
HTTP_HEADERS = {"Device-Token": secrets.TAGOIO_TOKEN}

DRM_UPLOAD = True
STREAM = "xbsl/loudness" #DRM
DRM_TRANSPORT = cloud.TRANSPORT_UDP # Digi Remote Manager protocol: cloud.TRANSPORT_TCP or cloud.TRANSPORT_UDP

MAX_COMMS_FAIL = 10 # number of consecutive communications failures before reset
INPUT_BUTTON = "D0" # button to shut down cellular component when long-pressed
STATUS_LED = "D4" # LED output pin for status messages
