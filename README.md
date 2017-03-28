# python-viessmann-tools

PKGBUILD and systemd unit files for Arch Linux are included, useful for ArchLinuxARM and RaspberryPi to monitor and reset Viessmann heaters

viessmanntools module includes a Vclient wrapper, VclientToMqtt and VitoReset

## vclient-to-mqtt
Query vcontrold periodically with vclient and publish results over MQTT

Needs python paho mqtt library, edit config values in /etc/viessmanntools.conf

## vclient-to-mqtt
Query vcontrold periodically with vclient and reset heater if error occured (needs a relay attached to the raspberrypi and soldered to the reset button of the heater)

Needs python paho mqtt library, edit config values in /etc/viessmanntools.conf
