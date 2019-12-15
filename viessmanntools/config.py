from configparser import ConfigParser


class ViessmannToolsConfig:
    @staticmethod
    def get_default_config():
        config = ConfigParser(interpolation=None)

        config["Vclient"] = {}
        config["Vclient"]["path"] = "/usr/bin/vclient"
        config["Vclient"]["vcontrold_host"] = "localhost:3002"
        config["Vclient"]["timeout"] = "30"

        config["VclientToMqtt"] = {}
        config["VclientToMqtt"][
            "commands"
        ] = "getTempAussen,getTempWarmwasser,getTempKessel,getBrennerLeistungFein,getBrennerStatus,getTempAbgas,getUmschaltventilStatus,getTempVorlauf"
        config["VclientToMqtt"]["query_period"] = "60"
        config["VclientToMqtt"][
            "unwanted_vclient_output"
        ] = '" Grad Celsius", " l/h", " %", " Stunden", " h"'
        config["VclientToMqtt"]["mqtt_broker"] = "192.168.224.1"
        config["VclientToMqtt"]["mqtt_port"] = "1883"
        config["VclientToMqtt"]["mqtt_tls"] = "False"
        config["VclientToMqtt"]["mqtt_username"] = ""
        config["VclientToMqtt"]["mqtt_password"] = ""
        config["VclientToMqtt"]["mqtt_topic"] = "tele/vclient-to-mqtt"

        config["VitoReset"] = {}
        config["VitoReset"]["gpio_pin"] = "12"
        config["VitoReset"]["query_period"] = "300"
        config["VitoReset"]["query_date_locale"] = "de_DE.UTF-8"
        config["VitoReset"]["query_date_format"] = "%a,%d.%m.%Y %H:%M:%S"
        config["VitoReset"]["allowed_codes"] = "00,F9,FF"
        config["VitoReset"]["reset_max"] = "3"
        config["VitoReset"]["mqtt_broker"] = "192.168.224.1"
        config["VitoReset"]["mqtt_port"] = "1883"
        config["VitoReset"]["mqtt_tls"] = "False"
        config["VitoReset"]["mqtt_username"] = ""
        config["VitoReset"]["mqtt_password"] = ""
        config["VitoReset"]["mqtt_topic"] = "tele/vito-reset"

        return config

    @staticmethod
    def get_config(config_file_path):
        config = ViessmannToolsConfig.get_default_config()
        config.read(config_file_path)

        return config
