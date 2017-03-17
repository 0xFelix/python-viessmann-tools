# vclient-tools

PKGBUILD and systemd unit files for Arch Linux are included, useful for ArchLinuxARM and RaspberryPi to monitor and reset Viessmann heaters

## vclient-to-mqtt
Query vcontrold periodically with vclient and publish results over MQTT

Needs python paho mqtt library, edit config values in /usr/bin/vclient-to-mqtt

## vclient-to-mqtt
Query vcontrold periodically with vclient and reset heater if error occured

Needs python paho mqtt library, edit config values in /usr/bin/vito-reset
