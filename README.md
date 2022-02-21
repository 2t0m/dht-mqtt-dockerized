# dht-mqtt-dockerized for HomeAssistant
A DHT22/DHT11 fully customisable python application running in a docker container to send temperature and humidty sensor values in a JSON format to a MQTT broker.
Initial code can be found on [Github](https://github.com/grigal/dht-mqtt-dockerized) and on [Docker Hub](https://hub.docker.com/r/tomasgrigaliunas/dht-mqtt-dockerized).

## Initial setup
In terms of hardware, you'll need a DHT11 or DHT22 temperature/humidity sensor connected to a Raspberry Pi. Examples can be found online depending on your specific models, one I would suggest would be [this one](https://www.instructables.com/Raspberry-Pi-Tutorial-How-to-Use-the-DHT-22/).

Additionally, you'll need to have [docker installed in your Raspberry Pi](https://phoenixnap.com/kb/docker-on-raspberry-pi).

If you already have everything setup, continue to the next section.

## Running docker container

### Using docker-compose
Requires docker-compose to be [installed on your Raspberry Pi](https://dev.to/rohansawant/installing-docker-and-docker-compose-on-the-raspberry-pi-in-5-simple-steps-3mgl).

Set a available configuration for the command in the `Available variables` section below and add the following to your `docker-compose.yml` file and run the `docker-compose up -d` command.
```
version: '3.3'
services:
    dht-mqtt-dockerized:
        build: .
        container_name: dht-mqtt-dockerized
        restart: unless-stopped
        network_mode: host
        privileged: true
        environment:
            SENSOR_PIN: '17'
            SENSOR_TYPE: 'dht22'
            SENSOR_CHECK_INTERVAL: '60'
            SENSOR_DECIMAL_DIGITS: '4'
            TEMP_DELTA: -1.2
            MQTT_HOSTNAME: localhost
            MQTT_PORT: 1883
            MQTT_TIMEOUT: 60
            MQTT_CLIENT_ID: 'dht22-mqtt'
            CLIENT_CLEAN_SESSION: 'False'
            CLIENT_TLS_INSECURE: 'False'
            MQTT_CLIENT_QOS: '4'
            MQTT_USERNAME: ''
            MQTT_PASSWORD: ''
            LOG_LEVEL: 'info'
```

### Available variables

- `SENSOR_PIN` - an integer for the Raspberry Pi pin to which the DHT Data pin is connected to (Default: `4`, refers to `GPIO4`).
- `SENSOR_TYPE` - refers to the DHT sensor type, available options are `DHT22` or `DHT11` (Default `DHT22`).
- `SENSOR_CHECK_INTERVAL` - the frequency in seconds on how often the temperature/humidity is checked by the sensor and sent to the MQTT broker (Default: `30`).
- `SENSOR_DECIMAL_DIGITS` - rounds the temperature/humidity values to the specified number (integer) of decimals (Default `2`).
- `TEMP_DELTA` - temperature delta to add to the sensor temperature before publishing.
- `MQTT_HOSTNAME` - the hostname or IP address of the MQTT broker to which the client should connect to, can be left empty if the broker is running on the same raspberry pi host (Default `localhost`).
- `MQTT_PORT` - the network port of the MQTT broker (Default `1883`)
- `MQTT_TIMEOUT` - maximum period in seconds allowed between communications with the broker (Default `60`)
- `MQTT_TOPIC` - the topic to which the temperature/humidity values in JSON should be published to (Default `sensor/value`).
- `MQTT_CLIENT_ID` - the `CLIENT_ID` of the MQTT Client (Default `dht-sensor-mqtt`).
- `CLIENT_CLEAN_SESSION` - defines whether the session is only stored in memory not persisted (Default `False`).
- `CLIENT_TLS_INSECURE` - defines verification of the server hostname in the server certificate.(Default `False`).
- `MQTT_CLIENT_QOS` - the quality of service level to use to publish with (Default `0`).
- `MQTT_USERNAME` - Set a username for broker authentication (Default ``).
- `MQTT_PASSWORD` - Set a password for broker authentication (Default ``).
- `LOG_LEVEL` - Sets the verbosity of the logs publishd to the console, available options are `debug`, `info`, `warn`, `error` (Default `info`).

## License
Eclipse Public License 2.0
