import os
import logging
import paho.mqtt.client as mqtt
import time
import json
import Adafruit_DHT as adafruit_dht

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
SENSOR_TYPE = os.getenv("SENSOR_TYPE", "DHT22").upper()
SENSOR_PIN = int(os.getenv('SENSOR_PIN', '4'))
SENSOR_CHECK_INTERVAL = int(os.getenv('SENSOR_CHECK_INTERVAL', 30))
DECIMAL_POINTS = int(os.getenv("SENSOR_DECIMAL_POINTS", 2))
TEMP_DELTA = float(os.getenv('TEMP_DELTA', 0))
MQTT_TEMP_CONFIG = "homeassistant/sensor/new_dht_temperature/config";
MQTT_TEMP_STATE = "homeassistant/sensor/new_dht_temperature/state";
MQTT_HUM_CONFIG = "homeassistant/sensor/new_dht_humidity/config";
MQTT_HUM_STATE = "homeassistant/sensor/new_dht_humidity/state";
MQTT_HOSTNAME = os.getenv("MQTT_HOSTNAME", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TIMEOUT = int(os.getenv("MQTT_TIMEOUT", 60))
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "dht-sensor-mqtt")
MQTT_CLEAN_SESSION = os.getenv("CLIENT_CLEAN_SESSION", False)
MQTT_TLS_INSECURE = os.getenv("CLIENT_TLS_INSECURE", True)
MQTT_CLIENT_QOS = int(os.getenv("CLIENT_QOS", 0))
MQTT_USERNAME = os.getenv('MQTT_USERNAME', None)
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', None)


def configure_logging():

    level_map={
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'WARN': logging.WARNING,
        'ERROR': logging.ERROR
    }

    log_level=level_map.get(LOG_LEVEL, "Unsupported log level provided!")
    logging.basicConfig(level=log_level)


def resolve_sensor_type():
    if SENSOR_TYPE is None:
        raise Exception('Sensor type not provided in the config file')

    if SENSOR_TYPE == 'DHT22':
        return adafruit_dht.DHT22
    elif SENSOR_TYPE == 'DHT11':
        return adafruit_dht.DHT11
    else:
        raise Exception("Supported sensor types: 'DHT22' and 'DHT11'")


def on_connect(client, userdata, flags, rc):
    logging.info("Connected to the MQTT broker!")


def on_disconnect(client, userdata, flags, rc):
    logging.warn(f"Disconnected from the MQTT broker. End state - '{rc}'")


if __name__ == '__main__':

    configure_logging()
    dht_sensor = resolve_sensor_type()

    if MQTT_HOSTNAME is None or MQTT_PORT is None:
        logging.error("Could not acquire MQTT broker connection parameters...")
        exit(1)

    client = mqtt.Client(MQTT_CLIENT_ID, MQTT_CLEAN_SESSION)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect

    client.connect(MQTT_HOSTNAME, MQTT_PORT, MQTT_TIMEOUT)

    client.loop_start()
    logging.info("Successfully initialized application! Let's try to read the sensor...")
    
    temp_data_conf = {
                "name": "DHT Temperature", "state_class": "measurement",
                "unique_id":"new_dht_temperature", "object_id":"new_dht_temperature",
                "unit_of_measurement": "°C", "device_class": "temperature",
                "state_topic": MQTT_TEMP_STATE,
                "retain": "true"
                }
    
    hum_data_conf = {
                "name": "DHT Humidity", "state_class": "measurement",
                "unique_id":"new_dht_humidity", "object_id":"new_dht_humidity",
                "unit_of_measurement": "%", "device_class": "humidity",
                "state_topic": MQTT_HUM_STATE,
                "retain": "true"
                }

    logging.info("Publishing homeassistant data configuration to "+MQTT_TEMP_CONFIG+" and "+MQTT_HUM_CONFIG)


    while True:
        try:
            
            client.publish(MQTT_TEMP_CONFIG, json.dumps(temp_data_conf))
            client.publish(MQTT_HUM_CONFIG, json.dumps(hum_data_conf))

            humidity, temperature = adafruit_dht.read_retry(dht_sensor, SENSOR_PIN)

            if humidity is not None and temperature is not None:

                logging.debug(f"Sensor values measured - temperature '{temperature}', humidity '{humidity}''")
                temp_data = round((temperature+TEMP_DELTA), DECIMAL_POINTS)
                hum_data = round(humidity, DECIMAL_POINTS)
                
                logging.debug("Publishing data to topics")
                client.publish(MQTT_TEMP_STATE, temp_data)
                client.publish(MQTT_HUM_STATE, hum_data)
            else:
                logging.error(f"Failed to read sensor values. Check you wiring and configuration. Retrying in {SENSOR_CHECK_INTERVAL}...")

        except Exception as e:
            logging.error(f"Something went wrong when trying to read the sensor and this shouldn't happen... Details: {e}")
        finally:
            time.sleep(SENSOR_CHECK_INTERVAL)
