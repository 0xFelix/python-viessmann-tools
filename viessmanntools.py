from json import dumps
from os import remove
from time import sleep
import configparser
import datetime
import locale
import subprocess
import re

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO

class ViessmannToolsConfig:
    @staticmethod
    def get_default_config():
        config = configparser.ConfigParser(interpolation=None)

        config["Vclient"] = {}
        config["Vclient"]["path"] = "/usr/bin/vclient"
        config["Vclient"]["vcontrold_host"] = "localhost:3002"
        config["Vclient"]["query_timeout"] = "30"

        config["VclientToMqtt"] = {}
        config["VclientToMqtt"]["query_data"] = "getTempAussen,getTempWarmwasser,getTempKessel,getBrennerLeistungFein,getBrennerStatus,getTempAbgas,getUmschaltventilStatus,getTempVorlauf"
        config["VclientToMqtt"]["query_period"] = "60"
        config["VclientToMqtt"]["value_separator"] = ";"
        config["VclientToMqtt"]["unwanted_vclient_output"] = '" Grad Celsius", " l/h", " %", " Stunden", " h"'
        config["VclientToMqtt"]["mqtt_broker"] = "192.168.222.36"
        config["VclientToMqtt"]["mqtt_topic"] = "tele/heater/STATE"

        config["VitoReset"] = {}
        config["VitoReset"]["gpio_pin"] = "8"
        config["VitoReset"]["query_period"] = "300"
        config["VitoReset"]["query_date_locale"] = "de_DE"
        config["VitoReset"]["query_date_format"] = "%a,%d.%m.%Y %H:%M:%S"
        config["VitoReset"]["allowed_errorcodes"] = "F9"
        config["VitoReset"]["reset_wait_time"] = "1"
        config["VitoReset"]["reset_max"] = "3"
        config["VitoReset"]["mqtt_broker"] = "192.168.222.36"
        config["VitoReset"]["mqtt_topic_reset"] = "tele/heater/RESET"
        config["VitoReset"]["mqtt_topic_vito_reset_state"] = "tele/heater/VITO-RESET-STATE"

        return config

    @staticmethod
    def get_config(config_file_path):
        config = ViessmanntoolsConfig.get_default_config()
        config.read(config_file_path)
        return config

class Vclient:
    def __init__(self, query_data, value_separator, config=None):
        if config is None:
            config = ViessmannToolsConfig.get_default_config()
        
        config = config["Vclient"]
        self.__query_timeout = config.getint("query_timeout")
        self.__encoding = locale.getpreferredencoding(False)

        commands = ""
        command_separator = ","
        template = ""
        for i, item in enumerate(query_data):
            if i == len(query_data) - 1:
                commands += item
                template += "$R" + str(i + 1)
            else:
                commands += item + command_separator
                template += "$R" + str(i + 1) + value_separator

        self.__template_filename = "/tmp/vclientTemplate_" + datetime.datetime.now().isoformat()
        with open(self.__template_filename, "w") as template_file:
            print(template, file=template_file)

        self.args = [config.get("path"), "-h", config.get("vcontrold_host"), "-t", self.__template_filename, "-c", commands]

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        remove(self.__template_filename)

    def run(self):
        result = subprocess.run(self.args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=self.__query_timeout, check=True, encoding=self.__encoding)

        result_lower = result.stdout.lower()
        if "framer: error 15" in result_lower:
            raise ValueError("Communication with heater was garbled, try again")
        elif "srv err" in result_lower or "error" in result_lower:
            raise RuntimeError("vclient execution failed, output was:\n" + result.stdout)

        return result.stdout

class VclientToMqtt:
    def __init__(self, config=None):
        if config is None:
            config = ViessmannToolsConfig.get_default_config()

        config = config["VclientToMqtt"]
        self.__query_data = config.get("query_data").split(",")
        self.__query_period = config.getint("query_period")
        self.__value_separator = config.get("value_separator")
        self.__unwanted_vclient_output = config.get("unwanted_vclient_output")[1:-1].split('", "')
        self.__mqtt_topic = config.get("mqtt_topic")

        self.__mqttc = mqtt.Client()
        self.__mqttc.connect(config.get("mqtt_broker"))
        self.__mqttc.loop_start()

        self.__run = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__mqttc.disconnect()

    def __sanitize_output(self, output):
        for item in self.__unwanted_vclient_output:
            output = output.replace(item, "")
        return output.rstrip()

    def run(self):
        self.__run = True

        with Vclient(query_data=self.__query_data, value_separator=self.__value_separator) as vclient:
            while self.__run:
                try:
                    vclient_results = self.__sanitize_output(vclient.run()).split(self.__value_separator)

                    data = {"Time" : datetime.datetime.now().isoformat(timespec="seconds")}
                    for i, item in enumerate(self.__query_data):
                        data[item] = vclient_results[i]

                    self.__mqttc.publish(self.__mqtt_topic, dumps(data), retain=True)
                except ValueError as value_error:
                    print(str(value_error))
                except subprocess.TimeoutExpired:
                    print("vclient query took too long, will try again next period")

                for _ in range(self.__query_period):
                    if not self.__run:
                        break
                    sleep(1)

    def stop(self):
        self.__run = False

class VitoReset():
    class State():
        OK = "OK"
        RESET_MAX_REACHED = "RESET_MAX_REACHED"
        NOT_ALLOWED_ERRORCODE = "NOT_ALLOWED_ERRORCODE"

    class VclientResult:
        def __init__(self, result, query_date_locale, query_date_format):
            locale.setlocale(locale.LC_TIME, query_date_locale)
            self.__query_date_format = query_date_format
            result_stripped = result.rstrip()
            second_space_index = self.__find_nth(result_stripped, " ", 2)
            self.error_datetime = self.__get_error_datetime(result_stripped[:second_space_index])
            self.errormsg = self.__get_errormsg(result_stripped[second_space_index + 1:])
            self.errorcode = self.__get_errorcode(result_stripped[second_space_index + 1:])

        def __str__(self):
            return str(self.__dict__)

        def __eq__(self, other):
            return self.__dict__ == other.__dict__

        @staticmethod
        def __find_nth(haystack, needle, n):
            start = haystack.find(needle)
            while start >= 0 and n > 1:
                start = haystack.find(needle, start + len(needle))
                n -= 1
            if start != -1:
                return start
            else:
                raise RuntimeError("Could not find nth character")

        @staticmethod
        def __get_errormsg(string):
            match = re.match(r".+?(?= \()", string)
            if match:
                return match.group(0)
            else:
                raise RuntimeError("Could not parse errormsg")

        @staticmethod
        def __get_errorcode(string):
            match = re.search(r"\(([^)]+)\)", string)
            if match:
                return match.group(1)
            else:
                raise RuntimeError("Could not parse errorcode")

        def __parse_date(self, date_string):
            try:
                return datetime.datetime.strptime(date_string, self.__query_date_format)
            except ValueError:
                raise RuntimeError("Could not parse datetime")

        def __get_error_datetime(self, string):
            return self.__parse_date(string)

    def __init__(self, config=None):
        if config is None:
            config = ViessmannToolsConfig.get_default_config()

        config = config["VitoReset"]
        self.__gpio_pin = config.getint("gpio_pin")
        self.__query_period = config.getint("query_period")
        self.__query_date_locale = config.get("query_date_locale")
        self.__query_date_format = config.get("query_date_format")
        self.__allowed_errorcodes = config.get("allowed_errorcodes").split(",")
        self.__reset_wait_time = config.getint("reset_wait_time")
        self.__reset_max = config.getint("reset_max")
        self.__mqtt_topic_reset = config.get("mqtt_topic_reset")
        self.__mqtt_topic_vito_reset_state = config.get("mqtt_topic_vito_reset_state")

        self.__setup_gpio()
        self.__mqttc = mqtt.Client()
        self.__mqttc.connect(config.get("mqtt_broker"))
        self.__mqttc.loop_start()

        self.__run = False

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.__mqttc.disconnect()

    def __set_gpio_output(self, output):
        print("Setting GPIO " + str(self.__gpio_pin) + " output to " + str(output))
        GPIO.output(self.__gpio_pin, output)

    def __setup_gpio(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.__gpio_pin, GPIO.OUT)
        self.__set_gpio_output(False)

    def __publish_reset(self, errorcode):
        self.__mqttc.publish(self.__mqtt_topic_reset, dumps({"Time" : datetime.datetime.now().isoformat(timespec="seconds"), "Errorcode" : errorcode}), retain=True)

    def __publish_vito_reset_state(self, state):
        self.__mqttc.publish(self.__mqtt_topic_vito_reset_state, dumps({"Time" : datetime.datetime.now().isoformat(timespec="seconds"), "State" : state}), retain=True)

    def __reset_vito(self, vclient_result):
        print("Resetting the heater")
        self.__publish_reset(vclient_result.errorcode)
        self.__set_gpio_output(True)
        sleep(self.__reset_wait_time)
        self.__set_gpio_output(False)

    def run(self):
        self.__run = True
        last_error = VitoReset.VclientResult("Do,01.01.1970 00:00:00 Geblaesedrehzahl bei Brennerstart zu niedrig (F9)")
        reset_counter = 0

        with Vclient(query_data=["getError0"], value_separator=";") as vclient:
            while self.__run:
                try:
                    vclient_result = VitoReset.VclientResult(vclient.run(), self.__query_date_locale, self.__query_date_format)
                    if vclient_result != last_error:
                        if vclient_result.errorcode in self.__allowed_errorcodes:
                            if reset_counter < self.__reset_max:
                                self.__reset_vito(vclient_result)
                                last_error = vclient_result
                                reset_counter += 1
                                self.__publish_vito_reset_state(VitoReset.State.OK)
                            else:
                                self.__publish_vito_reset_state(VitoReset.State.RESET_MAX_REACHED)
                                raise RuntimeError("reset_max reached, seems like your heater has more serious problems")
                        else:
                            raise RuntimeError("Current errorcode not in allowed_errorcodes, seems like your heater has more serious problems")
                    else:
                        reset_counter = 0
                        self.__publish_vito_reset_state(VitoReset.State.OK)
                except ValueError as value_error:
                    print(str(value_error))
                except subprocess.TimeoutExpired:
                    print("vclient query took too long, will try again next period")

                for _ in range(self.__query_period):
                    if not self.__run:
                        break
                    sleep(1)

    def stop(self):
        self.__run = False
