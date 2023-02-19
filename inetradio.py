#!/usr/bin/env python3

# tiny internet radio with Raspberry Zero WH and Pirate-Audi HAT
#
# init 20230218

import signal
import RPi.GPIO as GPIO
import sys
import os
from pathlib import Path
import time
from subprocess import Popen, DEVNULL

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import ST7789

configfile = "/home/pi/inetradio.cfg"

global stationcounter

try:
	with open( configfile, "r") as f:
		stationcounter = int(f.read())
		f.close()

except IOError:
	stationcounter = 0


# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, X and Y respectively
LABELS = ['A', 'B', 'X', 'Y']

PIN = {
	'A': 5,
	'B': 6,
	'X': 16,
	'Y': 24
}

# Set up RPi.GPIO with the "BCM" numbering scheme
GPIO.setmode(GPIO.BCM)


# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.
GPIO.setup(BUTTONS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

STATIONS = [
	[ "DLF Kultur", "http://st02.dlf.de/dlf/02/128/mp3/stream.mp3" ],
	[ "DLF", "http://st01.dlf.de/dlf/01/128/mp3/stream.mp3" ],
	[ "Kulturradio", "http://kulturradio.de/live.m3u" ],
	[ "Radio Eins", "http://www.radioeins.de/livemp3" ],
	[ "WDR 5", "https://www1.wdr.de/radio/wdr5/" ],
	[ "Ellinikos 93,2", "https://www1.wdr.de/radio/wdr5/" ],
	[ "JazzRadio B", "http://streaming.radio.co/s774887f7b/listen" ],
	[ "Cosmo", "http://wdr-cosmo-live.icecast.wdr.de/wdr/cosmo/live/mp3/128/stream.mp3" ],
	[ "Radio Gold", "https://radiogold-live.cast.addradio.de/radiogold/live/mp3/high/stream.mp3" ],
	[ "Left Coast", "http://somafm.com/seventies.pls" ],
	[ "Groove Salad", "http://ice1.somafm.com/groovesalad-128-mp3" ],
	[ "Caprice Minimalism", "http://213.141.131.10:8000/minimalism" ]
]

# Create ST7789 LCD display class for square LCD

# regarding backlight pin 13, read:
# https://github.com/pimoroni/pirate-audio/issues/31#issuecomment-678313017

disp = ST7789.ST7789(
        height=240,
        rotation=90,
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
        dc=9,
        backlight=13,               # 13 for Pirate-Audio; 18 for back BG slot, 19 for front BG slot.
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0,
        offset_top=0
    )

def stwrite(message):

	# Initialize display.
	disp.begin()

	WIDTH = disp.width
	HEIGHT = disp.height

	img = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
	size_x, size_y = draw.textsize(message, font)
	text_x = disp.width
	text_y = (disp.height - size_y) // 2

	t_start = time.time()

	# x = (time.time() - t_start) * 100
	# x %= (size_x + disp.width)

	draw.rectangle((0, 0, disp.width, disp.height), (0, 0, 0))
	draw.text((0, text_y), message, font=font, fill=(255, 255, 255))
	disp.display(img)


def stationplay(station):
	global proc

	try:
		# print("Killing pulseaudio and mplayer mplayer\n")

		proc.kill()
		os.system( "pulseaudio --kill 1>/dev/null 2>/dev/null" )

	except NameError:

		pass

	proc = Popen( [ 'mplayer', \
		'-loop', '0', '-allow-dangerous-playlist-parsing', \
		station ], \
		stdout = DEVNULL, stderr = DEVNULL )


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))

def playstation(stationcounter):
    station = STATIONS[stationcounter]
    stwrite( "[{0}] {1}".format(stationcounter, station[0]) )
    stationplay( station[1] )

def updstationcounter(stationcounter):
    f = open( configfile, "w")
    f.write(str(stationcounter))
    f.close()

def handle_radiobutton(pin):
    stationcounter = BUTTONS.index(pin)
    playstation(stationcounter)
    updstationcounter(stationcounter)

def handle_stationincrement_button(pin):
    global stationcounter
    stationcounter = (stationcounter+1) % len(STATIONS)
    playstation(stationcounter)
    updstationcounter(stationcounter)


# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 100ms to smooth out button presses.

# for pin in BUTTONS:
#    GPIO.add_event_detect(pin, GPIO.FALLING, handle_radiobutton, bouncetime=250)

GPIO.add_event_detect( PIN['A'], GPIO.FALLING, handle_radiobutton, bouncetime=250)
GPIO.add_event_detect( PIN['B'], GPIO.FALLING, handle_radiobutton, bouncetime=250)
GPIO.add_event_detect( PIN['X'], GPIO.FALLING, handle_radiobutton, bouncetime=250)
GPIO.add_event_detect( PIN['Y'], GPIO.FALLING, handle_stationincrement_button, bouncetime=250)


# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.

# for s in STATIONS:
#	print(s)

playstation(stationcounter)

signal.pause()
