#!/usr/bin/env python3

# pinetradio
# tiny internet radio with Raspberry Zero WH and Pirate-Audi HAT
#
# init 20230218

STATIONS = [
	[ "DLF Kultur", "http://st02.dlf.de/dlf/02/128/mp3/stream.mp3" ],
	[ "DLF", "http://st01.dlf.de/dlf/01/128/mp3/stream.mp3" ],
	[ "Kulturradio", "http://kulturradio.de/live.m3u" ],
	[ "Radio Eins", "http://www.radioeins.de/livemp3" ],
	[ "WDR 5", "http://wdr-wdr5-live.icecast.wdr.de/wdr/wdr5/live/mp3/128/stream.mp3" ],
	[ "Ellinikos 93,2", "http://netradio.live24.gr/orange9320" ],
	[ "JazzRadio Berlin", "http://streaming.radio.co/s774887f7b/listen" ],
	[ "WDR Cosmo", "http://wdr-cosmo-live.icecast.wdr.de/wdr/cosmo/live/mp3/128/stream.mp3" ],
	[ "Radio Gold", "https://radiogold-live.cast.addradio.de/radiogold/live/mp3/high/stream.mp3" ],
	[ "Left Coast", "http://somafm.com/seventies.pls" ],
	[ "Groove Salad", "http://ice1.somafm.com/groovesalad-128-mp3" ],
	[ "Caprice Minimalism", "http://213.141.131.10:8000/minimalism" ]
]

graceperiod = 2.0 # seconds

import signal
from threading import Timer
import RPi.GPIO as GPIO
import sys
import os
import re
import time
import subprocess
import psutil
import ST7789
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

configfile = "/home/pi/pinetradio.cfg"

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

# Create ST7789 LCD display class for square LCD

# regarding backlight pin 13, read:
# https://github.com/pimoroni/pirate-audio/issues/31#issuecomment-678313017

rotation = 270

disp = ST7789.ST7789(
        height=240,
        rotation=rotation,
        port=0,
        cs=ST7789.BG_SPI_CS_FRONT,  # BG_SPI_CS_BACK or BG_SPI_CS_FRONT
        dc=9,
        backlight=13,               # 13 for Pirate-Audio; 18 for back BG slot, 19 for front BG slot.
        spi_speed_hz=80 * 1000 * 1000,
        offset_left=0,
        offset_top=0
    )


def cleardisplay():
	global disp,img,draw

	# Initialize display.
	disp.begin()
	img = Image.new('RGB', (disp.width, disp.height), color="black")
	draw = ImageDraw.Draw(img)

def stwrite( position, message, font, color ):
	global disp,img,draw
	draw.text( position, message, font=font, fill=color)
	sizex, sizey = draw.textsize( message, font=font )
	return ( position[0]+sizex, position[1] )

# wrap text into display width
# https://stackoverflow.com/questions/8257147/wrap-text-in-pil
def get_wrapped_text(text: str, font: ImageFont.ImageFont,
                     line_length_in_pixels: int):
	lines = ['']

#	split and keep the separators:
	for word in re.split(r"([ /-])", text):

		word=word.strip()
		line = f'{lines[-1]} {word}'.strip()

		if ( font.getlength(line) > line_length_in_pixels ):
			lines.append(word)
		else:
			lines[-1] = line

		try:
			if ( word[-1] == "-" or word[-1] == "," or word[-1] == "/" ):
				lines.append('') # add a new line after "-" and ","
		except:
			pass

	cleanlines = []
	for line in lines:
		if not ( line == "" or line == "," or line == "-" or line == "/" ):
			cleanlines.append(line.strip())

	return '\n'.join(cleanlines)

def testsize( box, font_size, text):
	global disp,wrappedtext,font

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
	wrappedtext = get_wrapped_text( text, font, disp.width )
	size = font.getsize_multiline(wrappedtext)

	if ( (size is None)
		or ( size[0] >= box[2] - box[0] )
		or ( size[1] >= box[3] - box[1] ) ):
		return None
	else:
		return size

def bisectsize( box, a, b, text):

	span = b-a
	mid = (b-a) // 2

	if (mid >= 2 ):

		if ( testsize( box, a+mid, text ) is None ):
			return bisectsize( box, a, a+mid-1, text)

		else:
			return bisectsize( box, a+mid+1, b, text)

	else:
		if not ( testsize( box, b, text) is None ):
			return b

		if not ( testsize( box, a+mid, text) is None ):
			return a+mid

		if not ( testsize( box, a, text) is None ):
			return a

		else:
			return a-1


def writebox(draw, box, text, fontsize_min, fontsize_max):
	global disp,wrappedtext,font

	font_size = bisectsize( box, fontsize_min, fontsize_max, text )
	draw.multiline_text((box[0], box[2]), wrappedtext, anchor="ld", font=font, fill="cyan")


def stwrite3(message):
	global disp,img,draw

	newimg = img.copy()

	draw = ImageDraw.Draw(newimg)
	writebox( draw, ((0, 34, disp.height-1, disp.width-1)), message, fontsize_min=20, fontsize_max = 74)
	disp.display(newimg)


def stationplay(stationurl):
	global proc

	try:
		kill_processes(proc.pid)
		os.system( "pulseaudio --kill 1>/dev/null 2>/dev/null" )

	except NameError:
		pass

	volume = 100
	proc = subprocess.Popen( 'mplayer -volume {0} -allow-dangerous-playlist-parsing {1}'.format(volume,stationurl).split(),
		stdout = subprocess.PIPE, stderr = subprocess.DEVNULL )


def kill_processes(pid):
    '''Kills parent and children processess'''
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()

# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))

def playstation(stationcounter, graceful):
    global play,draw,disp

    station = STATIONS[stationcounter]

    cleardisplay()

    draw.rectangle( ((0, 0, disp.height-1, disp.width-1)), outline="yellow")

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    cursor = stwrite( (0,0), "{0}".format( stationcounter+1 ), font, "red" )
    cursor = stwrite( cursor, " {0}".format( station[0] ), font, "white" )

    disp.display(img)

    try:

        play.cancel()

    except NameError:

        pass

    if (graceful):

        play = Timer( graceperiod, stationplay, args=( station[1], ) )
        play.start()

    else:

        stationplay( station[1] )

def updstationcounter(stationcounter):
    f = open( configfile, "w")
    f.write(str(stationcounter))
    f.close()

def handle_radiobutton(pin):
    global stationcounter
    global play
    stationcounter = BUTTONS.index(pin)
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def handle_radiobutton0(pin):
    global stationcounter
    global play
    stationcounter = 0
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def handle_radiobutton1(pin):
    global stationcounter
    global play
    stationcounter = 1
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def handle_stationincrement_button(pin):
    global stationcounter
    global play
    stationcounter = (stationcounter+1) % len(STATIONS)
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def handle_stationdecrement_button(pin):
    global stationcounter
    global play
    stationcounter = (stationcounter-1) % len(STATIONS)
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

# Loop through out buttons and attach the "handle_button" function to each
# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
# picking a generous bouncetime of 100ms to smooth out button presses.

# for pin in BUTTONS:
#    GPIO.add_event_detect(pin, GPIO.FALLING, handle_radiobutton, bouncetime=250)

if rotation == 180:

	GPIO.add_event_detect( PIN['B'], GPIO.FALLING, handle_radiobutton0, bouncetime=250)
	GPIO.add_event_detect( PIN['Y'], GPIO.FALLING, handle_radiobutton1, bouncetime=250)
	GPIO.add_event_detect( PIN['A'], GPIO.FALLING, handle_stationincrement_button, bouncetime=250)
	GPIO.add_event_detect( PIN['X'], GPIO.FALLING, handle_stationdecrement_button, bouncetime=250)

elif rotation == 270:

	GPIO.add_event_detect( PIN['Y'], GPIO.FALLING, handle_radiobutton0, bouncetime=250)
	GPIO.add_event_detect( PIN['X'], GPIO.FALLING, handle_radiobutton1, bouncetime=250)
	GPIO.add_event_detect( PIN['B'], GPIO.FALLING, handle_stationincrement_button, bouncetime=250)
	GPIO.add_event_detect( PIN['A'], GPIO.FALLING, handle_stationdecrement_button, bouncetime=250)

else:

	GPIO.add_event_detect( PIN['A'], GPIO.FALLING, handle_radiobutton, bouncetime=250)
	GPIO.add_event_detect( PIN['B'], GPIO.FALLING, handle_radiobutton, bouncetime=250)
	GPIO.add_event_detect( PIN['X'], GPIO.FALLING, handle_stationincrement_button, bouncetime=250)
	GPIO.add_event_detect( PIN['Y'], GPIO.FALLING, handle_stationdecrement_button, bouncetime=250)

# Finally, since button handlers don't require a "while True" loop,
# we pause the script to prevent it exiting immediately.

# for s in STATIONS:
#	print(s)

playstation(stationcounter, graceful=False)
# draw.rectangle( ((0, 34, disp.height-1, disp.width-1)), outline="yellow")

# signal.pause()
while True:
	for stdoutline in proc.stdout:

		# print(stdoutline)

		if stdoutline.startswith(b'ICY Info:'):
			# ICY Info: StreamTitle='Nachrichten, ';
			try:
				res = re.search(r"ICY Info: StreamTitle=\'(.*?)\';", stdoutline.decode('UTF-8'))

				icyinfo = res.group(1)
			except:
				icyinfo = ""

			# print(icyinfo)
			stwrite3(icyinfo)
