from contextlib import contextmanager
from datetime import datetime
from enum import Enum
from json import dumps
from locale import LC_TIME, setlocale
from signal import SIGINT, SIGTERM, signal
from subprocess import TimeoutExpired
from time import sleep
from threading import Event
import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from .config import ViessmannToolsConfig
from .vclient import CommunicationGarbledError, Vclient


class VitoResetState(Enum):
    OK = "OK"
    RESET_MAX_REACHED = "RESET_MAX_REACHED"
    NOT_ALLOWED_CODE = "NOT_ALLOWED_CODE_"
    RESET = "RESET"


class HeaterState:
    def __init__(self, vclient_result, query_date_locale, query_date_format):
        self._query_date_locale = query_date_locale
        self._query_date_format = query_date_format

        result_str = vclient_result.rstrip()
        second_space_idx = self._find_nth(result_str, " ", 2)

        self.datetime = self._parse_datetime(result_str[:second_space_idx])
        self.msg = result_str[second_space_idx + 1 : -5]
        self.code = result_str[-3:-1]

    def __eq__(self, other):
        return (
            self.datetime == other.datetime
            and self.msg == other.msg
            and self.code == other.code
        )

    def _parse_datetime(self, date_str):
        with self._setlocale(self._query_date_locale):
            return datetime.strptime(date_str, self._query_date_format)

    @staticmethod
    @contextmanager
    def _setlocale(locale_str):
        saved = setlocale(LC_TIME)
        try:
            yield setlocale(LC_TIME, locale_str)
        finally:
            setlocale(LC_TIME, saved)

    @staticmethod
    def _find_nth(string, substr, nth):
        idx = string.find(substr)

        while idx >= 0 and nth > 1:
            idx = string.find(substr, idx + len(substr))
            nth -= 1

        if idx == -1:
            raise ValueError("Could not find nth occurence")

        return idx


class VitoReset:
    def __init__(self, config=None):
        if config is None:
            config = ViessmannToolsConfig.get_default_config()
        self._config = config
        config = config["VitoReset"]

        self._gpio_pin = config.getint("gpio_pin")
        self._query_period = config.getint("query_period")
        self._query_date_locale = config.get("query_date_locale")
        self._query_date_format = config.get("query_date_format")
        self._allowed_codes = config.get("allowed_codes").split(",")
        self._reset_max = config.getint("reset_max")
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

    def _setup_gpio(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self._gpio_pin, GPIO.OUT)
        self._set_gpio_output(False)

    def _set_gpio_output(self, output):
        print(f"Setting GPIO {self._gpio_pin} output to {output}", flush=True)
        GPIO.output(self._gpio_pin, output)

    def _publish_reset(self, code):
        self._mqtt_client.publish(
            f"{self._topic}/RESET",
            dumps(
                {"Time": datetime.now().isoformat(timespec="seconds"), "Code": code,}
            ),
            retain=True,
        )

    def _publish_state(self, state):
        self._mqtt_client.publish(
            f"{self._topic}/STATE",
            dumps(
                {"Time": datetime.now().isoformat(timespec="seconds"), "State": state,}
            ),
            retain=True,
        )

    def _reset_heater(self, code):
        print("Resetting the heater", flush=True)
        self._publish_reset(code)
        self._set_gpio_output(True)
        sleep(1)
        self._set_gpio_output(False)

    def _publish_state_and_exit(self, state, msg):
        print(msg, flush=True)
        self._publish_state(state)
        self._exit.set()

    def loop(self):
        self._connect_mqtt_client()
        self._setup_gpio()

        last_state = HeaterState(
            "Do,01.01.1970 00:00:00 Regelbetrieb (kein Fehler) (00)",
            self._query_date_locale,
            self._query_date_format,
        )
        reset_count = 0

        vclient = Vclient(["getError0"], self._config)
        first_run = True
        while first_run or not self._exit.wait(self._query_period):
            try:
                heater_state = HeaterState(
                    vclient.run(), self._query_date_locale, self._query_date_format,
                )

                if heater_state != last_state:
                    if heater_state.code in self._allowed_codes:
                        if reset_count < self._reset_max:
                            self._reset_heater(heater_state.code)
                            last_state = heater_state
                            reset_count += 1
                            self._publish_state(VitoResetState.RESET.value)
                        else:
                            self._publish_state_and_exit(
                                VitoResetState.RESET_MAX_REACHED.value,
                                "reset max reached, exiting",
                            )
                    else:
                        self._publish_state_and_exit(
                            f"{VitoResetState.NOT_ALLOWED_CODE.value}{heater_state.code}",
                            f"Code {heater_state.code} not allowed, exiting",
                        )
                else:
                    reset_count = 0
                    self._publish_state(VitoResetState.OK.value)
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
