from datetime import datetime
from json import dumps
from threading import Event
from signal import SIGINT, SIGTERM, signal
from subprocess import TimeoutExpired
import paho.mqtt.client as mqtt
from .config import ViessmannToolsConfig
from .vclient import CommunicationGarbledError, Vclient


class VclientToMqtt:
    def __init__(self, config=None):
        if config is None:
            config = ViessmannToolsConfig.get_default_config()
        self._config = config
        config = config["VclientToMqtt"]

        self._commands = config.get("commands").split(",")
        self._query_period = config.getint("query_period")
        self._unwanted_vclient_output = config.get("unwanted_vclient_output")[
            1:-1
        ].split('", "')
        self._host = config.get("mqtt_broker")
        self._port = config.getint("mqtt_port")
        self._tls = config.getboolean("mqtt_tls")
        self._username = config.get("mqtt_username")
        self._password = config.get("mqtt_password")
        self._topic = config.get("mqtt_topic")

        self._exit = Event()
        self._mqtt_client = mqtt.Client()

        signal(SIGINT, self._signal_handler)
        signal(SIGTERM, self._signal_handler)

    def _signal_handler(self, *_):
        self._exit.set()

    def _connect_mqtt_client(self):
        if self._username != "":
            if self._password != "":
                self._mqtt_client.username_pw_set(self._username, self._password)
            else:
                self._mqtt_client.username_pw_set(self._username)

        if self._tls:
            self._mqtt_client.tls_set()

        self._mqtt_client.will_set(f"{self._topic}/LWT", "Offline", retain=True)
        self._mqtt_client.connect(self._host, self._port)
        self._mqtt_client.loop_start()
        self._mqtt_client.publish(f"{self._topic}/LWT", "Online", retain=True)

    def _disconnect_mqtt_client(self):
        self._mqtt_client.publish(f"{self._topic}/LWT", "Offline", retain=True)
        self._mqtt_client.loop_stop()
        self._mqtt_client.disconnect()

    def _sanitize_output(self, output):
        for item in self._unwanted_vclient_output:
            output = output.replace(item, "")
        return output.rstrip()

    def loop(self):
        self._connect_mqtt_client()

        vclient = Vclient(self._commands, self._config)
        first_run = True
        while first_run or not self._exit.wait(self._query_period):
            try:
                results = self._sanitize_output(vclient.run()).split(";")

                data = {"Time": datetime.now().isoformat(timespec="seconds")}
                for i, cmd in enumerate(self._commands):
                    data[cmd] = results[i]

                self._mqtt_client.publish(f"{self._topic}/SENSOR", dumps(data))
            except CommunicationGarbledError as exc:
                print(exc, flush=True)
            except TimeoutExpired:
                print(
                    "vclient query took too long, will try again next period",
                    flush=True,
                )
            finally:
                first_run = False

        self._disconnect_mqtt_client()
