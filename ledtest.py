#!/usr/bin/env python3

from gpiozero import LED
from signal import pause
from time import sleep

# https://www.jeffgeerling.com/blogs/jeff-geerling/controlling-pwr-act-leds-raspberry-pi
# https://raspberrypi.stackexchange.com/questions/44004/control-pwr-and-act-leds-on-raspberry-pi-2-b-from-python
# https://github.com/gpiozero/gpiozero/issues/148

# Set the Pi Zero ACT LED trigger to 'none'.
# echo none | sudo tee /sys/class/leds/ACT/trigger

# Turn off the Pi Zero ACT LED.
# echo 0 | sudo tee /sys/class/leds/ACT/brightness

ACT = LED(47, active_high=True)
ACT.blink(5,0.2)

#while True:
#	print(ACT.is_lit)
#	sleep(.2)

pause()
