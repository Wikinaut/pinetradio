#!/usr/bin/env python3

# pinetradio tiny internet radio with Raspberry Zero WH and Pirate-Audio HAT
#
# requires an alsa device with dmix properties
#
#      20230325 version using apscheduler
#      20230318 version for mpv
# init 20230218


networkadapter="wlan0"

ambience="/home/pi/jukebox/ambientmixer/Ambientmix Bleiche VBR 80-120kbps.mp3"
minimal1="/home/pi/jukebox/minimal/Simeon ten Holt ‎- Canto Ostinato (1979) - Original 1984 Live Recording.mp3"
minimal2="/home/pi/jukebox/minimal/Arvo Pärt - Für Alina (1976).mp3"

beepsound = "/home/pi/sounds/beep.wav"
servicebellsound = "/home/pi/sounds/service-bell-receptionsklingel.wav"
gongsound1 = "/home/pi/sounds/Glockenturm1.wav"
gongsoundlast = "/home/pi/sounds/GlockenturmLast.wav"


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
buttonBacklightTimeout = 20
mutedBacklightTimeout = 5
icyBacklightTimeout = 10
showtimeTimeout = 5
short_showtimeTimeout = 1.5
watchdogTimeout = 15 # Test
showtime_every_n_seconds = 60

# after mute:
# whether volume buttons immediately control volume
# or first press only restart backlight display
volumebutton_after_mute_direct = False

global dict

# words longer than this will be tried to hyphenate
global maxwordlength
maxwordlength = 14

# max length of first hyphenated part of a word
global maxpartialwordlength
maxpartialwordlength=8

global anybuttonpressed
anybuttonpressed = False

volumesteps = [ 0, 5, 8, 10, 12, 15, 17, 20,
	22, 25, 28, 30, 35, 40, 45, 50, 55,
	60, 65, 70, 75, 80, 85, 90, 95, 100 ]

startvolstep = 4

# Code for special operations (sequence of pin numbers)

code5656 = [5,6,5,6] # restart WiFi

code5566 = [5,5,6,6]
code55566 = [5,5,5,6,6]
code555566 = [5,5,5,5,6,6]

global last_icyinfo
last_icyinfo = ""

global icyinfo
icyinfo= ""

# Test speakers
# aplay -L
# speaker-test -Dplughw:CARD=sndrpihifiberry,DEV=0 -c2 -s1
# speaker-test -Dplughw:CARD=sndrpihifiberry,DEV=0 -c2 -s2

# for PI OS LITE (32 bit) install:
#
#

# sudo apt install git libi2c-dev
# sudo raspi-config
#   Interface Options: enable SPI for LCD-display
#                      enable I2C for DAC
# sudo reboot now

# https://domoticproject.com/extending-life-raspberry-pi-sd-card/
#
# setup /tmp as a RAM disk
#
# sudo nano /etc/fstab
#
#    add a line:
#    tmpfs /tmp tmpfs defaults,size=50M 0 0


# disable swapping and check zero-byte swap file
#
# https://community.element14.com/products/raspberry-pi/f/forum/20159/how-do-i-permanently-disable-the-swap-service/151444
# sudo nano /etc/dphys-swapfile
# change CONF_SWAPSIZE=0
#
# After reboot
# confirm that no swap exists by checking that the Swap line of the following command is 0:
# sudo free -h


# disable wifi_powersave

# sudo nano /etc/network/interfaces
#
#   interfaces(5) file used by ifup(8) and ifdown(8)
#   Include files from /etc/network/interfaces.d:
#   source /etc/network/interfaces.d/*
#   allow-hotplug wlan0
#   iface wlan0 inet manual
#   post-up iw wlan0 set power_save off

# check that wifi_powersave is really off
# iw wlan0 get power_save
# should report: "Power save: off"

# enable the pirate radio DAC audio output
# and you can better also disable raspi onboard audio.
#
# see https://github.com/pimoroni/pirate-audio
# see https://shop.pimoroni.com/products/pirate-audio-line-out
#
# sudo nano /boot/config.txt
#   dtoverlay=hifiberry-dac
#   gpio=25=op,dh
#   dtparam=audio=off

# sudo apt install mpv libmpv-dev python3-mpv libasound2-plugin-equal

# make sure not to have pulseaudio and vlc and mplayer
# sudo apt remove pulseaudio vlc mplayer

# pip install pyphen st7789

# use the ~/.asoundrc file

# check:
#
# aplay -l
# aplay -L
# alsamixer -D equal

# usually not needed:
# alsactl kill rescan

# List all audiodevices
# mpv --audio-device=help
#
# Test
# mpv --audio-device=alsa/plugmixequal http://www.radioeins.de/livemp3 --volume=50 --cache=no

# check not to have any display manager onboad, otherwise stop and disable
# ps -ef | grep dm
# sudo systemctl stop lightdm
# sudo systemctl disable lightdm
# sudo systemctl stop cups
# sudo systemctl disable cups


# optional:
#
# crontab -e
#   * * * * * /home/pi/network.py >> /tmp/wifi.log
#
# sudo crontab -e
#   NOW=date +%Y%m%d-%H%M%S
#   */15 * * * * /usr/local/bin/wifi_reconnect.sh
#   @reboot echo "`$NOW` -- boot --" > /var/log/wifi_reconnect


import mpv

# we import this big libraries - at the latest moment, after playing
# lazy loading later
# import pyphen
# import apscheduler

import signal
from threading import Timer, Thread
import RPi.GPIO as GPIO
import sys
import os
import re
import time
from datetime import datetime
import subprocess
import ST7789
from PIL import Image, ImageDraw, ImageFont
import socket

stationcfgfile = "/home/pi/pinetradio.station.cfg"
volumecfgfile = "/home/pi/pinetradio.volume.cfg"

global stationcounter
global volumedecrementbuttonblock
volumedecrementbuttonblock = False

global hostname
hostname = os.uname()[1]

def tick():
	print('Tick! The time is: %s' % datetime.now())


def playsound(volumepercent=100, soundfile=beepsound):

	nowtime=timenow()
	# print( f"{nowtime} playsound {soundfile} ({volumepercent} %)")
	soundplayer.volume=volumepercent*player.volume/100
	soundplayer.play(soundfile)
	soundplayer.wait_for_playback()

def threadedPlaysoundFunction(volumepercent,soundfile):
	playsound(volumepercent,soundfile)

def beepwait(volumepercent=100,soundfile=beepsound):
	playsound(volumepercent,soundfile)

def beep(volumepercent=100,soundfile=beepsound):
	t = Thread( target=threadedPlaysoundFunction, daemon=True, args=( volumepercent,soundfile ) )
	t.start()

def servicebell(volumepercent=25,soundfile=servicebellsound):
	t = Thread( target=threadedPlaysoundFunction, daemon=True, args=( volumepercent,soundfile ) )
	t.start()

def gong1Function(volumepercent):
	playsound(volumepercent,gongsoundlast)

def gong1(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong1Function, daemon=True, args=( volumepercent, ) )
	t.start()

def gong2Function(volumepercent):
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsoundlast)

def gong2(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong2Function, daemon=True, args=( volumepercent, ) )
	t.start()

def gong3Function(volumepercent):
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsoundlast)

def gong3(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong3Function, daemon=True, args=( volumepercent, ) )
	t.start()

def gong4Function(volumepercent):
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsoundlast)

def gong4(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong4Function, daemon=True, args=( volumepercent, ) )
	t.start()

def threadedBeep3Function(volumepercent):
	playsound(volumepercent,beepsound)
	time.sleep(0.5)
	playsound(volumepercent,beepsound)
	time.sleep(0.5)
	playsound(volumepercent,beepsound)

def beep3(volumepercent=50):
	t = Thread( target=threadedBeep3Function, daemon=True, args=(volumepercent, ) )
	t.start()

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


# Get signal strength and basic network adapter parameters

def get_networkinfo(interface="wlan0"):

    proc = subprocess.Popen(
	["/usr/sbin/iwlist", interface, "scan"],
	stdout=subprocess.PIPE,
	universal_newlines=True)
    out, err = proc.communicate()
    out = out.split("\n")

    for i, val in enumerate(out):

        if 'Signal' in val:
            signal_line = val.split()
            if 'Signal' in signal_line:
                rssi = int(signal_line[signal_line.index('Signal')+1].split('=')[1])

        if 'ESSID' in val:
            ssid_line = val.split('"')
            ssid = ssid_line[1]

        hostname = socket.gethostname()
        ipaddr= socket.gethostbyname(hostname)

    return hostname,ipaddr,ssid,rssi


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

global buttonqueue
buttonqueue = []

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
	return currentDateAndTime.strftime("%Y%m%d%H%M%S")

def timenow():
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
		or ( size[0] > box[2] - box[0] + 1 )
		or ( size[1] > box[3] - box[1] + 1 ) ):
		return None
	else:
		return size

def bisectsize( box, a, b, text):

	# returns the optimal maximum font_size to fully fill the part of the display
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

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", font_size)
	wrappedtext = get_wrapped_text( text, font, disp.width )

	draw.multiline_text((box[0], box[2]), wrappedtext, anchor="ld", font=font, fill="cyan")

def stwrite3(message):
	global disp,img,stationimg,logger

	hostname,ipaddr,ssid,rssi = get_networkinfo(networkadapter)

	logger.warning(f"{message} ({rssi} db)")

	stationimg = img.copy()
	draw = ImageDraw.Draw(stationimg)

	writebox( draw, ((0, 34, disp.height-1, disp.width-1)), message + " (–" + str(-rssi) + " db)", fontsize_min=20, fontsize_max = 70)
	disp.display(stationimg)

def stationplay(stationurl):

	global stationselecttimer,last_icyinfo

	stwrite3("[ Gönnen Sie sich eine Pause - die Musiktitel kommen gleich! ]")
	last_icyinfo=""

	try:
		stationselecttimer.cancel()
	except:
		pass

	if player.mute:
		startvolume = 0
	else:
		startvolume = 1.0*volumesteps[vol]

	player.volume = startvolume
	logger.warning(f"{stationurl}")
	player.play(stationurl)


def kill_processes():
	global watchdogtimer

	os.system( "pulseaudio --kill 1>/dev/null 2>/dev/null" )

	try:
		watchdogtimer.cancel()

	except:
		pass


# "handle_button" will be called every time a button is pressed
# It receives one argument: the associated input pin.
def handle_button(pin):
    label = LABELS[BUTTONS.index(pin)]
    print("Button press detected on pin: {} label: {}".format(pin, label))

def sendvolume(volume):
	player.volume = 1.0*volume

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
		if player.mute:
			timeout = mutedBacklightTimeout
		else:
			timeout = buttonBacklightTimeout

	return not retriggerbacklight(dutycycle=100,timeout=timeout)

def handle_stationincrement_button(pin):
	global stationcounter

	buttonpressed(pin)

	if player.mute:
		player.mute = False
		setvol(vol, graceful=False, show=True)

	if triggerdisplay():
		return

	stationcounter = (stationcounter+1) % len(STATIONS)
	updstationcounter(stationcounter)
	playstation(stationcounter, graceful=True)


def handle_stationdecrement_button(pin):
	global stationcounter

	buttonpressed(pin)

	if player.mute:
		player.mute = False
		setvol(vol, graceful=False, show=True)

	if triggerdisplay():
		return

	stationcounter = (stationcounter-1) % len(STATIONS)
	updstationcounter(stationcounter)
	playstation(stationcounter, graceful=True)

def showcurrentimg():
	global volimg,stationimg
	disp.display(stationimg)

def showtime(timeout=short_showtimeTimeout,force=False):
	global showtimetimer

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

	hostname,ipaddr,ssid,rssi = get_networkinfo(networkadapter)

	timeimg = Image.new('RGB', (disp.width, disp.height), color="blue")
	draw = ImageDraw.Draw(timeimg)

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
	draw.text( ( 120, 70 ),
		"{0}\n{3}\n{1}\n{2}\n{4}\n{5} dB".
		format(hostname,githash[0],githash[1],ipaddr,ssid,rssi),
		font=font, fill="white", anchor="mm" )

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
	draw.text( ( 120, 160 ),
		"{0}".format(timenow()), font=font, fill="white", anchor="mm" )
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

def seqmatch(needle,haystack):

	ln=len(needle)
	lh=len(haystack)

	for i in range(lh-ln+1):
		if needle==haystack[i:i+ln]:
			return True
	return False

def bptimerhandler(pin):
	global anybuttonpressed,buttonqueue
	anybuttonpressed = False
	buttonqueue.clear()

def restartWifi():

	logger.warning("code5656 detected")
	soundplayer.wait_for_playback() # wait finishing previous beep

	beepwait()

	logger.warning("pausing player and soundplayer")

	player.mute=True
	soundplayer.mute=True

	player.pause=True
	soundplayer.pause=True

	stwrite3("restarting the WiFi")
	os.system('sudo ifdown --force wlan0')

	time.sleep(1)
	os.system('sudo ifup wlan0')
	time.sleep(1)

	logger.warning("un-pausing player and soundplayer")

	player.pause=False
	soundplayer.pause=False

	player.mute=False
	soundplayer.mute=False

	beep()


def buttonpressed(pin):
	global anybuttonpressed,bptimer,buttonqueue
	anybuttonpressed = True
	buttonqueue.append(pin)
	beep(volumepercent=50)

	if seqmatch(code5656,buttonqueue):
		buttonqueue.clear()
		restartWifi()
		return

	if seqmatch(code555566,buttonqueue):
		buttonqueue.clear()
		player.play(minimal2)
		player.loop_file="inf"
		cleardisplay()
		stwrite3(minimal2)
		return

	if seqmatch(code55566,buttonqueue):
		buttonqueue.clear()
		player.play(minimal1)
		player.loop_file="inf"
		cleardisplay()
		stwrite3(minimal1)
		return

	if seqmatch(code5566,buttonqueue):
		buttonqueue.clear()
		player.play(ambience)
		player.loop_file="inf"
		cleardisplay()
		stwrite3(ambience)
		return

	try:
		bptimer.cancel()

	except:
		pass

	# suppress showtime for 90 seconds after the last key press
	bptimer = Timer( 90, bptimerhandler, args = (pin, ) )
	bptimer.start()

def handle_volumeincrement_button(pin):
	global vol

	buttonpressed(pin)

	if player.mute:
		player.mute = False
		setvol(vol, graceful=False, show=True)
		triggerdisplay()
		if not volumebutton_after_mute_direct:
			return
	elif not display_is_on():
			triggerdisplay()
			return

	if vol < len(volumesteps)-1:
		vol += 1
		savevol(vol)
		setvol(vol, graceful=False, show=True)

def gracetimer():
	global volumedecrementbuttonblock
	volumedecrementbuttonblock = False

def blockvolumedecrementbutton():
	global volumedecrementbuttonblock

	volumedecrementbuttonblock = True
	try:
		grace.cancel()
	except:
		grace = Timer( 0.3, gracetimer, args = () )
		grace.start()

def handle_volumedecrement_button(pin):
	global vol,grace,volumedecrementbuttonblock

	buttonpressed(pin)

	if volumedecrementbuttonblock:
		return
	blockvolumedecrementbutton()

	display_was_on = display_is_on()

	if player.mute:
		player.mute = False
		setvol(vol, graceful=False, show=True)
		triggerdisplay()
		if not volumebutton_after_mute_direct:
			return

	starttime = time.time()

#	while GPIO.input(pin) == 0 and time.time()-starttime < 1:
#		time.sleep(0.2)

	time.sleep(0.2) # debounce
	while GPIO.input(pin) == 0 and time.time()-starttime < 1:
		time.sleep(0.2)

	if time.time()-starttime >= 1:

		if player.mute:

			player.mute = False

			triggerdisplay()
			if not volumebutton_after_mute_direct:
				return

		else:

			player.mute = True

			img = Image.new('RGB', (disp.width, disp.height), color="blue")
			draw = ImageDraw.Draw(img)

			font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
			draw.text( ( 120, 80),
				"muted", font=font, fill="white", anchor="mm" )

			font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
			draw.text( ( 120, 160 ),
				"{0}".format(timenow()), font=font, fill="white", anchor="mm" )

			disp.display(img)

			beep3()

			triggerdisplay(timeout=10)

			while GPIO.input(pin) == 0 and time.time()-starttime < 5:
				time.sleep(0.2)

			if time.time()-starttime > 5:

				cleardisplay()
				triggerdisplay()

				killer.killed = True
				killer.shutdown = True

			else:

				time.sleep(10-time.time()+starttime)
				showtime(timeout=10,force=True)
				return

	else:
		triggerdisplay()

		if vol > 0:
			vol -= 1
			savevol(vol)
			setvol(vol, graceful=False, show=True)


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
	if not player.mute:
		playstation(stationcounter, graceful=False)


def shutdown():

	beep3()
	setbacklight(100)

	img = Image.new('RGB', (disp.width, disp.height), color="black")
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
	draw.text( ( 120, 120), "shutdown sequence started…", font=font, fill="white", anchor="mm" )
	disp.display(img)

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

	player.quit()
	soundplayer.quit()

	if killer.shutdown:
		print("Shutdown")
		os.system("sudo shutdown -h now")
	return

def triggerwatchdog():
	global watchdogtimer

	try:
		watchdogtimer.cancel()
	except:
		pass

	if not killer.killed:
		watchdogtimer = Timer( watchdogTimeout, restart, args=() )
		watchdogtimer.start()


def make_observer(player_name):
	def observer(_prop_name, prop_val):
		global last_icyinfo

		# print(f'{player_name}: {prop_val}')

		try:
			icyinfo = prop_val['icy-title']
			# print( now() + " " + icyinfo )

			if icyinfo != last_icyinfo:

				# Test
				# correct max font_size = 28
				# icyinfo="Erdbeben-Hilfe mit Hindernissen: Enttäuschung bei Türken und Kurden in Berlin, Luise Sammann"

				stwrite3(icyinfo)
				retriggerbacklight(dutycycle=100,timeout=icyBacklightTimeout)
				last_icyinfo = icyinfo

		except:
			pass

	return observer

def soundplayer_is_playing():
	return not soundplayer.core_idle

def player_is_playing():
	return not player.core_idle


def playnews(newsstationcount=0):
	global stationcounter

	# only switch to station if not yet playing
	if newsstationcount != stationcounter:
		playstation(newsstationcount, graceful=False)

		# resume playing the previous station (stationcounter)
		# in n seconds
		timer_resumeplay = Timer( 5*60, resumeplay, args=( stationcounter, newsstationcount ) )
		timer_resumeplay.start()

def resumeplay(laststation, newsstationcount):
	global stationcounter

	# switch to the currently selected station
	# except when the user selected the newsstation when this was played
	# In this case, a station change is not needed
	if stationcounter != newsstationcount:
		playstation(stationcounter, graceful=False)

def setup_scheduler():
	newsstation = 0
	schedule_playnews = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_playnews.add_job(playnews, 'cron', second=0, minute=0, args=( newsstation, ) )

#	https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
#	https://apscheduler.readthedocs.io/en/stable/modules/triggers/date.html
#
#	Example for a certain time/date
#	schedule_playnews.add_job(playnews, 'date', run_date=datetime(2023, 03, 25, 20, 0, 0), args=( 0, ) )

	schedule_playnews.start()

	schedule_showtime = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_showtime.add_job(showtime, 'cron', minute="*")
	schedule_showtime.start()

	schedule_gong1 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong1.add_job(gong1, 'cron', minute=15)
	schedule_gong1.start()

	schedule_gong2 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong2.add_job(gong2, 'cron', minute=30)
	schedule_gong2.start()

	schedule_gong3 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong3.add_job(gong3, 'cron', minute=45)
	schedule_gong3.start()

	schedule_gong4 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong4.add_job(gong4, 'cron', minute=0)
	schedule_gong4.start()


if __name__ == '__main__':

	# set mpv options to use the *mixing* alsa channel

	# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=898575
	# https://medium.com/intrasonics/robust-continuous-audio-recording-c1948895bb49
	# https://wiki.ubuntuusers.de/mpv/

	# Remark:
	# 'stream_lavf_o' : 'reconnect_streamed=1,reconnect_delay_max=300,reconnect_at_eof=1',
	# does not work with playlist urls/files such as http://somafm.com/seventies.pls

	options= {
		'audio_device' : 'alsa/plugmixequal',
		'volume_max' : '1000.0',
		'keep_open' : 'no',
		'idle' : 'yes',
		'gapless_audio' : 'weak',
		'audio_buffer' : '0.2',
		'network_timeout' : '60',
		'stream_lavf_o' : 'reconnect_streamed=1,reconnect_delay_max=300',
		'cache-secs' : '5',
		'demuxer_thread' : 'yes',
		'demuxer_readahead_secs' : '5',
		'demuxer_max_bytes' : '2MiB',
		'load_unsafe_playlists' : 'yes'
	}

	player = mpv.MPV( **options )
	# player.audio_buffer = 3.0

	soundplayer = mpv.MPV( **options )

	servicebell()

	setupdisplay()
	setup_button_handlers()

	killer = GracefulKiller()
	kill_processes()

	import logging
	import mylogger
	logger = mylogger.setup( "WARNING", "/tmp/pinetradio.log" )

	playstation(stationcounter, graceful=False)
	player.observe_property('metadata', make_observer('player'))

	logger.warning(f"mpv options: {options}")
	import tzlocal
	from apscheduler.schedulers.background import BackgroundScheduler
	setup_scheduler()

	starttime= time.time()
	logger.warning("Import of pyphen started.")
	import pyphen
	dict = pyphen.Pyphen(lang='de_DE')
	deltat= time.time()-starttime
	logger.warning(f"pyphen imported, loading of de_DE took {deltat:.2f} seconds on Raspberry Pi Zero")

	starttime = time.time()

	while not killer.killed:
		time.sleep(0.5)
		# triggerwatchdog()

	print("\nShutdown signal received.")
	shutdown()
	print("End of the program. I was killed gracefully :)")
