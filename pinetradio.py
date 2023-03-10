#!/usr/bin/env python3

# pinetradio tiny internet radio with Raspberry Zero WH and Pirate-Audi HAT
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

graceperiod = 2.0 # seconds between new station is actually selected
buttonBacklightTimeout = 10
mutedBacklightTimeout = 3
icyBacklightTimeout = 10
showtimeTimeout = 4
short_showtimeTimeout = 1.5
watchdogTimeout = 15 # Test
showtime_every_n_seconds = 60

# after mute:
# whether volume buttons immediately control volume
# or first press only restart backliight display
volumebutton_after_mute_direct = True

global dict

# words longer than this will be tried to hyphenate
global maxwordlength
maxwordlength = 16

# max length of first hyphenated part of a word
global maxpartialwordlength
maxpartialwordlength=10

global anybuttonpressed
anybuttonpressed = False

volumesteps = [ 0, 0.25, 0.5, 0.75, 1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 85, 100 ]

startvolstep = 4
muted = False

global last_icyinfo
last_icyinfo = ""

global icyinfo
icyinfo= ""

# Test speakers
# aplay -L
# speaker-test -Dplughw:CARD=sndrpihifiberry,DEV=0 -c2 -s1
# speaker-test -Dplughw:CARD=sndrpihifiberry,DEV=0 -c2 -s2

# sudo apt install mpv sox libsox-fmt-mp3 libasound2-plugin-equal
# apt remove pulseaudio vlc chromium-browser

# edit ~/.asoundrc

# alsactl kill rescan
# alsamixer -D equal

# Test
# mpv --audio-device=alsa/plugmixequal http://www.radioeins.de/livemp3 --volume=50 --cache=no

# ps -ef | grep dm
# sudo systemctl stop lightdm
# sudo systemctl disable lightdm

import pyphen
import signal
from threading import Timer
import RPi.GPIO as GPIO
import sys
import os
import re
import time
from datetime import datetime
import math
import subprocess
import psutil
import ST7789
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

stationcfgfile = "/home/pi/pinetradio.station.cfg"
volumecfgfile = "/home/pi/pinetradio.volume.cfg"

global stationcounter
global volumedecrementbuttonblock
volumedecrementbuttonblock = False

global hostname
hostname = os.uname()[1]

def get_git_revision_short_hash() -> str:
	# return subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD'],
	return subprocess.check_output(['git',
	'log','-1', '--date=format:%Y%m%d-%H%M', '--format=%ad %h'],
	cwd=os.path.dirname(os.path.realpath(__file__))).decode('ascii').strip().split()

global githash
githash = get_git_revision_short_hash()

try:
	with open( stationcfgfile, "r") as f:
		stationcounter = int(f.read())
		f.close()

except IOError:
	stationcounter = 0

try:
	with open( volumecfgfile, "r") as f:
		vol = int(f.read())
		f.close()

except IOError:
	vol = startvolstep

# https://stackoverflow.com/questions/18499497/how-to-process-sigterm-signal-gracefully
class GracefulKiller:

	killed = False
	shutdown = False

	def __init__(self):
		signal.signal(signal.SIGINT, self.exit_gracefully)
		signal.signal(signal.SIGTERM, self.exit_gracefully)

	def exit_gracefully(self, *args):
		self.killed = True


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
# Standard display setup for Pirate Audio, except we omit the backlight pin
SPI_SPEED_MHZ = 90
rotation = 270

# regarding backlight pin 13, read:
# https://github.com/pimoroni/pirate-audio/issues/31#issuecomment-678313017

disp = ST7789.ST7789(
        height=240,
	rotation=rotation,		# Needed to display the right way up on Pirate Audio
	port=0,				# SPI port
	# cs=1,				# SPI port Chip-select channel
	cs=ST7789.BG_SPI_CS_FRONT,	# BG_SPI_CS_BACK or BG_SPI_CS_FRONT
	dc=9,				# BCM pin used for data/command
	backlight=None,			# We'll control the backlight ourselves
	# backlight=13,			# 13 for Pirate-Audio; 18 for back BG slot, 19 for front BG slot.
	spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000,
        offset_left=0,
        offset_top=0
)

def now():
	currentDateAndTime = datetime.now()
	return currentDateAndTime.strftime("%H:%M:%S")

def cleardisplay():
	global img,draw,stationimg
	img = Image.new('RGB', (disp.width, disp.height), color="black")
	stationimg = img.copy()
	draw = ImageDraw.Draw(img)

def showvolume(draw,volcolor="red",restcolor="yellow"):
	total = len(volumesteps)-1
	length = disp.height*(total-vol) // total
	draw.line( (disp.width-1,disp.height-1,disp.width-1,length), fill=volcolor )
	draw.line( (disp.width-1,length-1,disp.width-1,0), fill=restcolor )

def setupdisplay():
	global disp,img,draw,backlight,display

	# Initialize display.
	# disp.begin()

	GPIO.setmode(GPIO.BCM)

	# We must set the backlight pin up as an output first
	GPIO.setup(13, GPIO.OUT)

	# Set up our pin as a PWM output at 500Hz
	backlight = GPIO.PWM(13, 100)
	display = 100

	# Start the PWM at 100% duty cycle
	# backlight.start(100)
	triggerdisplay()

	# brightness = 50
	# backlight.ChangeDutyCycle(brightness)
	# backlight.stop()

	cleardisplay()
	draw.rectangle( ((0, 0, disp.height-1, disp.width-1)), outline="yellow")

def setbacklight(dutycycle):
	global backlight,display
	display=dutycycle
	backlight.ChangeDutyCycle(dutycycle)

def display_is_on():
	global display
	return display > 0

def retriggerbacklight(dutycycle=100,timeout=buttonBacklightTimeout):
	# returns True if backlight was on

	global backlighttimer,display

	try:
		is_backlightOn = not backlighttimer.finished.is_set()
		backlighttimer.cancel()

	except:
		is_backlightOn = True

	backlight.start(dutycycle)
	display = dutycycle
	backlighttimer = Timer( timeout, setbacklight, args=( 0, ) )
	backlighttimer.start()

	return is_backlightOn

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

	text2=['']
	for word in re.split(r"([ /-])", text):
		if len(word) > maxwordlength:
			wx = dict.wrap(word,maxpartialwordlength)
			if wx:
				text2.append(wx[0].strip())
				text2.append(wx[1].strip())
			else:
				# none indicates: no hyphenation possible
				text2.append(word.strip())
		else:
			text2.append(word.strip())

	text3 = " ".join(text2)

#	split and keep the separators:
#	for word in re.split(r"([ /-])", text3):
	for word in re.split(r"([ ])", text3):

		word=word.strip()

		line = f'{lines[-1]} {word}'.strip()

		if ( font.getlength(line) > line_length_in_pixels ):
			lines.append(word)
		else:
			lines[-1] = line

		try:
			# this is apparently no longer needed
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
		or ( size[0] > box[2] - box[0] )
		or ( size[1] > box[3] - box[1] ) ):
		return None
	else:
		return size

def bisectsize( box, a, b, text):

	# returns the optimal font_size
	# textsize() sets the global wrappedtext

	mid = abs(b-a) // 2

	if (mid == 0 ):

		if not ( testsize( box, b, text) is None ):
			return b

		if not ( testsize( box, a, text) is None ):
			return a

		else:
			testsize( box, a-1, text)
			return a-1
	else:

		if ( testsize( box, a+mid, text ) is None ):
			return bisectsize( box, a, a+mid-1, text)
		else:
			return bisectsize( box, a+mid+1, b, text)


def writebox(draw, box, text, fontsize_min, fontsize_max):
	global disp,wrappedtext,font

	font_size = bisectsize( box, fontsize_min, fontsize_max, text )
	draw.multiline_text((box[0], box[2]), wrappedtext, anchor="ld", font=font, fill="cyan")

def stwrite3(message):
	global disp,img,stationimg

	stationimg = img.copy()

	draw = ImageDraw.Draw(stationimg)
	writebox( draw, ((0, 34, disp.height-1, disp.width-1)), message, fontsize_min=20, fontsize_max = 70)
	disp.display(stationimg)

def send_command(command):
	try:
		print(command, flush=True, file=proc.stdin)
	except:
		pass

def stationplay(stationurl):
	global proc

	icyinfo = ""

	LINE_BUFFERED = 1

	try:
		stationselecttimer.cancel()
	except:
		pass

	try:
		kill_processes()

	except NameError:
		pass

	if muted:
		startvolume = 0
	else:
		startvolume = volumesteps[vol]

	proc = subprocess.Popen('/usr/bin/mplayer -slave -idle -allow-dangerous-playlist-parsing -volume {0} 1 {1}'
		.format(startvolume,stationurl).split(),
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.DEVNULL,
		universal_newlines=True, bufsize=LINE_BUFFERED)

	time.sleep(10) # wait for mplayer start up

	if muted:
		send_command("mute 1")
	else:
		send_command("mute 0")
		sendvolume(startvolume)


def kill_processes():
	global proc,watchdogtimer,backlighttimer,showtimetimer,volumetimer,stationselecttimer

	try:
		'''Kills parent and children processess'''
		parent = psutil.Process(proc.pid)
		for child in parent.children(recursive=True):
        		child.kill()
		parent.kill()

	except NameError:
		pass

	os.system( "pulseaudio --kill 1>/dev/null 2>/dev/null" )

	try:
		watchdogtimer.cancel()
#		backlightimer.cancel()
#		showtimetimer.cancel()
#		volumetimer.cancel()
#		stationselecttimer.cancel()

	except:
		pass


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))

def sendvolume(volume):
	send_command( 'volume {} 1'.format(volume))

def setvol(vol, graceful, show=False):
	global volumetimer,disp,img,stationimg,volimg

	volimg = stationimg.copy()
	draw = ImageDraw.Draw(volimg)
	showvolume(draw)
	if show:
		disp.display(volimg)

	volume = volumesteps[vol]

	try:
		volumetimer.cancel()

	except NameError:

		pass

	if (graceful):

		volumetimer = Timer( 0.2, sendvolume, args=( volume, ) )
		volumetimer.start()

	else:
		sendvolume( volume )


def playstation(stationcounter, graceful):
    global stationselecttimer,draw,disp,img,stationimg

    station = STATIONS[stationcounter]

    cleardisplay()
    draw.rectangle( ((0, 0, disp.height-1, disp.width-1)), outline="yellow")

    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
    cursor = stwrite( (0,0), "{0}".format( stationcounter+1 ), font, "red" )
    cursor = stwrite( cursor, " {0}".format( station[0] ), font, "white" )

    stationimg = img.copy()
    showvolume(draw)
    disp.display(img)

    try:
        stationselecttimer.cancel()

    except NameError:
        pass

    if (graceful):

        stationselecttimer = Timer( graceperiod, stationplay, args=( station[1], ) )
        stationselecttimer.start()

    else:

        stationplay( station[1] )

def updstationcounter(stationcounter):
    f = open( stationcfgfile, "w")
    f.write(str(stationcounter))
    f.close()

def handle_radiobutton(pin):
    global stationcounter
    stationcounter = BUTTONS.index(pin)
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def handle_radiobutton0(pin):
    global stationcounter
    stationcounter = 0
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def handle_radiobutton1(pin):
    global stationcounter
    stationcounter = 1
    updstationcounter(stationcounter)
    playstation(stationcounter, graceful=True)

def triggerdisplay(timeout=None):
	if timeout is None:
		if muted:
			timeout = mutedBacklightTimeout
		else:
			timeout = buttonBacklightTimeout

	return not retriggerbacklight(dutycycle=100,timeout=timeout)

def handle_stationincrement_button(pin):
	global stationcounter,muted

	buttonpressed(pin)

	if muted:
		muted = False
		send_command("mute 0")
		send_command("play")
		setvol(vol, graceful=False, show=True)

	if triggerdisplay():
		return

	stationcounter = (stationcounter+1) % len(STATIONS)
	updstationcounter(stationcounter)
	playstation(stationcounter, graceful=True)


def handle_stationdecrement_button(pin):
	global stationcounter,muted

	buttonpressed(pin)

	if muted:
		muted = False
		send_command("mute 0")
		send_command("play")
		setvol(vol, graceful=False, show=True)

	if triggerdisplay():
		return

	stationcounter = (stationcounter-1) % len(STATIONS)
	updstationcounter(stationcounter)
	playstation(stationcounter, graceful=True)

def showcurrentimg():
	global volimg,stationimg
	try:
		disp.display(volimg)
	except:
		disp.display(stationimg)

def showtime(timeout=short_showtimeTimeout,force=False):
	global stationimg,showtimetimer

	# suppress time display when a button was pressed recently

	if anybuttonpressed and not force:
		return

	is_showtimeOn = False

	try:
		is_showtimeOn = not showtimetimer.finished.is_set()
	except:
		is_showtimeOn = False

	if is_showtimeOn:
		try:
			showtimetime.cancel()
		except:
			pass

	timeimg = Image.new('RGB', (disp.width, disp.height), color="blue")
	draw = ImageDraw.Draw(timeimg)
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 22)
	draw.text( ( 120, 50 ),
		"{0}\n{1}\n{2}".format(hostname,githash[0],githash[1]), font=font, fill="white", anchor="mm" )
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
	draw.text( ( 120, 160 ),
		"{0}".format(now()), font=font, fill="white", anchor="mm" )
	showvolume(draw,"white","black")
	disp.display(timeimg)

	retriggerbacklight(timeout=timeout)

	if not is_showtimeOn or force:
		showtimetimer = Timer( timeout+1.0, showcurrentimg, args=() )
		showtimetimer.start()

def savevol(vol):
	f = open( volumecfgfile, "w")
	f.write(str(vol))
	f.close()

def bptimerhandler(pin):
	global anybuttonpressed
	anybuttonpressed = False
	# print("buttontimer ends pin",pin)

def buttonpressed(pin):
	global anybuttonpressed
	anybuttonpressed = True
	# print("buttontimer starts pin",pin)

	bptimer = Timer( 20, bptimerhandler, args = (pin, ) )
	bptimer.start()

def handle_volumeincrement_button(pin):
	global vol,muted

	buttonpressed(pin)

	if muted:
		muted = False
		send_command("mute 0")
		# send_command("play")
		setvol(vol, graceful=False, show=True)
		triggerdisplay()
		if not volumebutton_after_mute_direct:
			return
	elif triggerdisplay():
			return

	if vol < len(volumesteps)-1:
		vol += 1
		savevol(vol)
		setvol(vol, graceful=False, show=True)

	# showtime()


def gracetimer():
	global volumedecrementbuttonblock
	volumedecrementbuttonblock = False

def blockvolumedecrementbutton():
	global volumedecrementbuttonblock

	volumedecrementbuttonblock = True
	try:
		grace.cancel()
	except:
		grace = Timer( 2, gracetimer, args = () )
		grace.start()

def handle_volumedecrement_button(pin):
	global vol,muted,grace,volumedecrementbuttonblock

	buttonpressed(pin)

	if volumedecrementbuttonblock:
		return

	display_was_on = display_is_on()

	if muted:
		muted = False
		send_command("mute 0")
		# send_command("play")
		setvol(vol, graceful=False, show=True)
		triggerdisplay()
		if not volumebutton_after_mute_direct:
			return

	starttime = time.time()

	while GPIO.input(pin) == 0 and time.time()-starttime < 1:
		time.sleep(0.2)

	if time.time()-starttime >= 1:

		if muted:

			muted = False
			send_command("mute 0")
			# send_command("play")
			triggerdisplay()
			if not volumebutton_after_mute_direct:
				return

		else:

			blockvolumedecrementbutton()

			muted = True
			send_command("mute 1")
			# send_command("stop")

			img = Image.new('RGB', (disp.width, disp.height), color="blue")
			draw = ImageDraw.Draw(img)

			font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
			draw.text( ( 120, 80),
				"muted", font=font, fill="white", anchor="mm" )

			font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
			draw.text( ( 120, 160 ),
				"{0}".format(now()), font=font, fill="white", anchor="mm" )

			disp.display(img)
			triggerdisplay(timeout=7)

			while GPIO.input(pin) == 0 and time.time()-starttime < 4:
				time.sleep(0.2)

			if time.time()-starttime > 4:

				cleardisplay()
				triggerdisplay()

				killer.killed = True
				killer.shutdown = True

				# shutdown()

			else:
				time.sleep(5-time.time()+starttime)
				showtime(timeout=2,force=True)
				return

	else:
		triggerdisplay()

		if vol > 0:
			vol -= 1
			savevol(vol)
			setvol(vol, graceful=False, show=True)

	# showtime()	# after volume may be changed


def setup_button_handlers():
	# Loop through out buttons and attach the "handle_button" function to each
	# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
	# picking a generous bouncetime of 100ms to smooth out button presses.

	# for pin in BUTTONS:
	#    GPIO.add_event_detect(pin, GPIO.FALLING, handle_radiobutton, bouncetime=250)

	try:
		GPIO.remove_event( PIN['Y'] )
	except:
		pass

	GPIO.add_event_detect( PIN['Y'], GPIO.FALLING, handle_stationincrement_button, bouncetime=250)

	try:
		GPIO.remove_event( PIN['X'] )
	except:
		pass

	GPIO.add_event_detect( PIN['X'], GPIO.FALLING, handle_stationdecrement_button, bouncetime=250)

	try:
		GPIO.remove_event( PIN['B'] )
	except:
		pass

	GPIO.add_event_detect( PIN['B'], GPIO.FALLING, handle_volumeincrement_button, bouncetime=250)

	try:
		GPIO.remove_event( PIN['A'] )
	except:
		pass

	GPIO.add_event_detect( PIN['A'], GPIO.FALLING, handle_volumedecrement_button, bouncetime=250)

def restart():

	# TODO log this

	if not muted:
		playstation(stationcounter, graceful=False)


def shutdown():

	print("End of the program. I was killed gracefully :)")

	setbacklight(100)

	img = Image.new('RGB', (disp.width, disp.height), color="red")
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
	draw.text( ( 120, 120), "Good\nbye", font=font, fill="white", anchor="mm" )
	disp.display(img)

	kill_processes()
	time.sleep(1)

	def big(text):

		img = Image.new('RGB', (disp.width, disp.height), color="black")
		draw = ImageDraw.Draw(img)
		font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 270)
		draw.text( ( 120, 120), text, font=font, fill="white", anchor="mm" )
		disp.display(img)
		time.sleep(0.2)

	big("3")
	big("2")
	big("1")
	big("0")
	setbacklight(0)
	backlight.stop()
	cleardisplay()
	disp.display(img)

	if killer.shutdown:
		print("Shutdown")
		os.system("sudo shutdown -h now")

	sys.exit()

def triggerwatchdog():
	global watchdogtimer

	try:
		watchdogtimer.cancel()
	except:
		pass

	if not killer.killed:
		watchdogtimer = Timer( watchdogTimeout, restart, args=() )
		watchdogtimer.start()

if __name__ == '__main__':

	dict = pyphen.Pyphen(lang='de_DE')

	setupdisplay()
	setup_button_handlers()

	killer = GracefulKiller()

	kill_processes()
	playstation(stationcounter, graceful=False)

	starttime = time.time()

	while not killer.killed:

		for stdoutline in proc.stdout:

			triggerwatchdog()

			it = int( time.time() % showtime_every_n_seconds )
			if it == 0:
				showtime()

			if killer.killed:
				break

			try:
				setup_button_handlers()
			except:
				pass

			if stdoutline.startswith('ICY Info:'):

				try:
					res = re.search(r"ICY Info: StreamTitle=\'(.*?)\';", stdoutline)
					icyinfo = res.group(1)
				except:
					pass
					# icyinfo = ""

				if icyinfo != last_icyinfo:

					stwrite3(icyinfo)
					retriggerbacklight(dutycycle=100,timeout=icyBacklightTimeout)
					last_icyinfo = icyinfo

	shutdown()
	print("Ende.")
