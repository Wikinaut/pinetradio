#!/usr/bin/env python3

from gpiozero import LED
from signal import pause
from time import sleep

# https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
# https://raspberrypi.stackexchange.com/questions/44004/control-pwr-and-act-leds-on-raspberry-pi-2-b-from-python
# https://github.com/gpiozero/gpiozero/issues/148
# https://netzmafia.ee.hm.edu/skripten/hardware/RasPi/RasPi_OnboardLED.html
# https://www.heelpbook.net/2021/raspberry-pi-controlling-pwr-and-act-leds-red-and-green-leds/
# https://n.ethz.ch/~dbernhard/disable-led-on-a-raspberry-pi.html systemd service

# Set the Pi Zero ACT LED trigger to 'none'.
# echo none | sudo tee /sys/class/leds/ACT/trigger

# Turn off the Pi Zero ACT LED.
# echo 0 | sudo tee /sys/class/leds/ACT/brightness

# or see disable-led.service
# sudo systemctl enable disable-led

ACT = LED(47, active_high=False)
ACT.off()
sleep(5)
ACT.on()
sleep(5)
ACT.off()

ACT.blink(0.5,5)

#while True:
#	print(ACT.is_lit)
#	sleep(.2)

pause()
