#!/usr/bin/env python3

# pinetradio tiny internet radio with Raspberry Zero WH and Pirate-Audio HAT
#
# requires an alsa device with dmix properties
# because we need to play a stream and additional signals like beeps
#
#
#      20230731 2-key-rollover for all four buttons
#      20230416 using pigpio
#      20230325 using apscheduler
#      20230318 version for mpv
# init 20230218


networkadapter="wlan0"

ambience="/home/pi/jukebox/ambientmixer/Ambientmix Bleiche VBR 80-120kbps.mp3"
minimal1="/home/pi/jukebox/minimal/Simeon ten Holt ‎- Canto Ostinato (1979) - Original 1984 Live Recording.mp3"
minimal2="/home/pi/jukebox/minimal/Arvo Pärt - Für Alina (1976).mp3"
minimal3="/home/pi/jukebox/shepard.mp3"
minimal4="/home/pi/jukebox/BCC CCC Pausenmucke - Fear of Ghosts - Machine Lullaby.mp3"

beepsound = "/home/pi/sounds/beep.wav"
quindar1sound = "/home/pi/sounds/Quindar1.wav"
quindar2sound = "/home/pi/sounds/Quindar2.wav"
quindar1soundshort = "/home/pi/sounds/Quindar1short.wav"
quindar2soundshort = "/home/pi/sounds/Quindar2short.wav"
servicebellsound = "/home/pi/sounds/service-bell-receptionsklingel.wav"
gongsound1 = "/home/pi/sounds/Glockenturm1.wav"
gongsoundlast = "/home/pi/sounds/GlockenturmLast.wav"


STATIONS = [
	[ "DLF Kultur", "http://st02.dlf.de/dlf/02/128/mp3/stream.mp3" ],
	[ "DLF", "http://st01.dlf.de/dlf/01/128/mp3/stream.mp3" ],
	[ "Kulturradio", "http://kulturradio.de/live.m3u" ],
	[ "Radio Eins", "http://www.radioeins.de/livemp3" ],
	[ "WDR 5", "http://wdr-wdr5-live.icecast.wdr.de/wdr/wdr5/live/mp3/128/stream.mp3" ],
	[ "JazzRadio Berlin", "http://streaming.radio.co/s774887f7b/listen" ],
	[ "WDR Cosmo", "http://wdr-cosmo-live.icecast.wdr.de/wdr/cosmo/live/mp3/128/stream.mp3" ],
	[ "Ellinikos 93,2", "http://netradio.live24.gr/orange9320" ],
	[ "Left Coast", "http://somafm.com/seventies.pls" ],
	[ "Groove Salad", "http://ice1.somafm.com/groovesalad-128-mp3" ],
	[ "Heavyweight Reggae", "http://somafm.com/reggae.pls" ],
	[ "DEF CON Radio", "https://somafm.com/defcon.pls" ],
	[ "Radio Gold", "https://radiogold-live.cast.addradio.de/radiogold/live/mp3/high/stream.mp3" ],
	[ "Caprice Minimalism", "http://213.141.131.10:8000/minimalism" ]
]

graceperiod = 2.0 # seconds between new station is actually selected
buttonBacklightTimeout = 30
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
code6565 = [6,5,6,5] # restart player

code5566 = [5,5,6,6]
code55566 = [5,5,5,6,6]
code555566 = [5,5,5,5,6,6]
code5555566 = [5,5,5,5,5,6,6]
code55555566 = [5,5,5,5,5,5,6,6]

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
#
# Best practice: disable the system logging
# sudo systemctl disable rsyslog

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
import pigpio
import sys
import os
import re
import time
from datetime import datetime
import subprocess
import ST7789
from PIL import Image, ImageDraw, ImageFont
import socket
import json

cfgfile ="/home/pi/pinetradio.cfg"

global stationcounter
global volstep
global muted

global volumedecrementbuttonblock
volumedecrementbuttonblock = False

global hostname
hostname = os.uname()[1]

stationfont = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 28)
font20 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
font46 = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)

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

def quindar1wait(volumepercent=100,soundfile=quindar1sound):
	playsound(volumepercent,soundfile)
	logger.warning("quindar1wait")

def quindar2wait(volumepercent=100,soundfile=quindar2sound):
	playsound(volumepercent,soundfile)
	logger.warning("quindar2wait")

def beep(volumepercent=100,soundfile=beepsound):
	t = Thread( target=threadedPlaysoundFunction, daemon=True, args=( volumepercent,soundfile ) )
	t.start()

def quindar1(volumepercent=100,soundfile=quindar1soundshort):
	t = Thread( target=threadedPlaysoundFunction, daemon=True, args=( volumepercent,soundfile ) )
	t.start()

def quindar2(volumepercent=100,soundfile=quindar2soundshort):
	t = Thread( target=threadedPlaysoundFunction, daemon=True, args=( volumepercent,soundfile ) )
	t.start()

def servicebell(volumepercent=25,soundfile=servicebellsound):
	t = Thread( target=threadedPlaysoundFunction, daemon=True, args=( volumepercent,soundfile ) )
	t.start()

def servicebellwait(volumepercent=100,soundfile=servicebellsound):
	playsound(volumepercent,soundfile)
	logger.warning("servicebellwait")

def gong1Function(volumepercent):
	if muted:
		return
	playsound(volumepercent,gongsoundlast)

def gong1(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong1Function, daemon=True, args=( volumepercent, ) )
	t.start()

def gong2Function(volumepercent):
	if muted:
		return
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsoundlast)

def gong2(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong2Function, daemon=True, args=( volumepercent, ) )
	t.start()

def gong3Function(volumepercent):
	if muted:
		return
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsound1)
	playsound(volumepercent,gongsoundlast)

def gong3(volumepercent=70,soundfile=gongsound1):
	t = Thread( target=gong3Function, daemon=True, args=( volumepercent, ) )
	t.start()

def gong4Function(volumepercent):
	if muted:
		return
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


global cfgdata

try:
	with open( cfgfile, "r") as f:
		cfgdata = json.load(f)
		stationcounter=cfgdata['station']
		volstep=cfgdata['volstep']
		muted=cfgdata['muted']
		f.close()

except IOError:

	stationcounter=0
	volstep=startvolstep
	muted=False

	cfgdata = {
		'station': stationcounter,
		'volstep' : startvolstep,
		'muted': muted
	}


steady = 20000 # microseconds

pressed = pigpio.LOW
released = pigpio.HIGH

class TwoButtons():

	def __init__(self,
			button1,button2,button3,button4,
			callback1,callback2,callback3,callback4,
			callback12,callback13,callback14,
			callback23,callback24,
			callback34):

		self.last = ""

		# get a pigpio instance
		self.pi = pigpio.pi()

		# set up buttons
		self.button1 = button1
		self.button2 = button2
		self.button3 = button3
		self.button4 = button4

		# set up glitch filter to debounce each switch
		self.pi.set_glitch_filter(self.button1, steady)
		self.pi.set_glitch_filter(self.button2, steady)
		self.pi.set_glitch_filter(self.button3, steady)
		self.pi.set_glitch_filter(self.button4, steady)

		# set up each button as an input
		self.pi.set_mode(self.button1, pigpio.INPUT)
		self.pi.set_mode(self.button2, pigpio.INPUT)
		self.pi.set_mode(self.button3, pigpio.INPUT)
		self.pi.set_mode(self.button4, pigpio.INPUT)

		# create a callback for when button is pressed
		self.pi.callback(self.button1, pigpio.EITHER_EDGE, self.button_pressed)
		self.pi.callback(self.button2, pigpio.EITHER_EDGE, self.button_pressed)
		self.pi.callback(self.button3, pigpio.EITHER_EDGE, self.button_pressed)
		self.pi.callback(self.button4, pigpio.EITHER_EDGE, self.button_pressed)

		self.callback1 = callback1
		self.callback2 = callback2
		self.callback3 = callback3
		self.callback4 = callback4
		self.callback12 = callback12
		self.callback13 = callback13
		self.callback14 = callback14
		self.callback23 = callback23
		self.callback24 = callback24
		self.callback34 = callback34

	def clrlast_cb(self):
		self.last = ""

	def callbackTwo(self,both,pin,level,tick):

		if both != self.last:

			self.last = both
			clrlastTimer = Timer( 0.1, self.clrlast_cb, args=() )
			clrlastTimer.start()

			if both == "12":
				self.callback12(pin,level,tick)
			elif both == "13":
				self.callback13(pin,level,tick)
			elif both == "14":
				self.callback14(pin,level,tick)
			elif both == "23":
				self.callback23(pin,level,tick)
			elif both == "24":
				self.callback24(pin,level,tick)
			elif both == "34":
				self.callback34(pin,level,tick)


	# common button press callback for both buttons
	def button_pressed(self, pin, level, tick):

		both = None

		if pin == self.button1:

			if level == pressed:

				for _ in range(10):
					if self.pi.read(self.button2) == pressed:
						both = "12"
						break
					if self.pi.read(self.button3) == pressed:
						both = "13"
						break
					if self.pi.read(self.button4) == pressed:
						both = "14"
						break
					time.sleep(0.005)

				if not both:
					if self.pi.read(self.button1) == pressed:
						self.callback1(pin,level,tick)
					if self.pi.read(self.button2) == pressed:
						self.callback2(pin,level,tick)
					if self.pi.read(self.button3) == pressed:
						self.callback3(pin,level,tick)
					if self.pi.read(self.button4) == pressed:
						self.callback4(pin,level,tick)

				if both:
					self.callbackTwo(both,pin,level,tick)

		elif pin == self.button2:

			if level == pressed:

				for _ in range(10):
					if self.pi.read(self.button1) == pressed:
						both = "12"
						break
					if self.pi.read(self.button3) == pressed:
						both = "23"
						break
					if self.pi.read(self.button4) == pressed:
						both = "24"
						break
					time.sleep(0.005)

				if not both:
					if self.pi.read(self.button1) == pressed:
						self.callback1(pin,level,tick)
					if self.pi.read(self.button2) == pressed:
						self.callback2(pin,level,tick)
					if self.pi.read(self.button3) == pressed:
						self.callback3(pin,level,tick)
					if self.pi.read(self.button4) == pressed:
						self.callback4(pin,level,tick)

				if both:
					self.callbackTwo(both,pin,level,tick)

		elif pin == self.button3:

			if level == pressed:

				for _ in range(10):
					if self.pi.read(self.button1) == pressed:
						both = "13"
						break
					if self.pi.read(self.button2) == pressed:
						both = "23"
						break
					if self.pi.read(self.button4) == pressed:
						both = "34"
						break
					time.sleep(0.005)

				if not both:
					if self.pi.read(self.button1) == pressed:
						self.callback1(pin,level,tick)
					if self.pi.read(self.button2) == pressed:
						self.callback2(pin,level,tick)
					if self.pi.read(self.button3) == pressed:
						self.callback3(pin,level,tick)
					if self.pi.read(self.button4) == pressed:
						self.callback4(pin,level,tick)

				if both:
					self.callbackTwo(both,pin,level,tick)

		elif pin == self.button4:

			if level == pressed:

				for _ in range(10):
					if self.pi.read(self.button1) == pressed:
						both = "14"
						break
					if self.pi.read(self.button2) == pressed:
						both = "24"
						break
					if self.pi.read(self.button3) == pressed:
						both = "34"
						break
					time.sleep(0.005)

				if not both:
					if self.pi.read(self.button1) == pressed:
						self.callback1(pin,level,tick)
					if self.pi.read(self.button2) == pressed:
						self.callback2(pin,level,tick)
					if self.pi.read(self.button3) == pressed:
						self.callback3(pin,level,tick)
					if self.pi.read(self.button4) == pressed:
						self.callback4(pin,level,tick)

				if both:
					self.callbackTwo(both,pin,level,tick)

# Get signal strength and basic network adapter parameters

def get_networkinfo_raw(interface="wlan0"):

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
        ipaddr = socket.gethostbyname(hostname)

    return hostname,ipaddr,ssid,rssi

def get_networkinfo(interface="wlan0"):

	ipaddr = None
	connectionwaslost = False

	while ipaddr is None:

		try:
			# try to get an ip addr
			hostname,ipaddr,ssid,rssi = get_networkinfo_raw(interface)
		except:
			if not connectionwaslost:
				noiptime = time.time()
				logger.warning("*** reconnecting: waiting for ip")
				connectionwaslost = True
			time.sleep(1.0)

	# we only print the regained ip addr when we were disconnected
	# we do not print the addr in normal program flow
	if connectionwaslost:
		deltatime = 1.0 + time.time() - noiptime
		logger.warning(f"*** without ip: {deltatime:.1f} seconds")
		logger.warning(f"*** ip after reconnect: {ipaddr}")

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

# Activity LED on Raspberry Pi Zero is BCM pin 47
ACT = 47

global buttonqueue
buttonqueue = []

pi = pigpio.pi()       # pi accesses the local Pi's GPIO

pi.write(ACT, 1)
pi.set_mode(ACT, pigpio.OUTPUT)

# Buttons connect to ground when pressed, so we should set them up
# with a "PULL UP", which weakly pulls the input signal to 3.3V.

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
	length = disp.height*(total-volstep) // total
	draw.line( (disp.width-1,disp.height-1,disp.width-1,length), fill=volcolor )
	draw.line( (disp.width-1,length-1,disp.width-1,0), fill=restcolor )

def setupdisplay():
	global disp,img,draw,display

	# We must set the backlight pin up as an output first
	pi.set_mode(13, pigpio.OUTPUT)

	# Set up our pin as a PWM output at 1000Hz
	pi.set_PWM_frequency(13, 1000)
	display = 100

	triggerdisplay()

	cleardisplay()
	draw.rectangle( ((0, 0, disp.height-1, disp.width-1)), outline="yellow")
	stwrite3("[ Pinetradio started ]")

def setbacklight(dutycycle):
	global display
	display=dutycycle
	pi.set_PWM_dutycycle(13, dutycycle*255/100)

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

	pi.set_PWM_dutycycle(13, dutycycle*255/100)
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

	message = message.strip(', ')
	logger.warning(f"{message} ({rssi} db)")

	if muted:
		return

	stationimg = img.copy()
	draw = ImageDraw.Draw(stationimg)

	writebox( draw, ((0, 34, disp.height-1, disp.width-1)), message + " (–" + str(-rssi) + " db)", fontsize_min=20, fontsize_max = 70)
	disp.display(stationimg)

def stationplay(stationnr):

	global stationselecttimer,draw

	draw.rectangle( ((0, 0, disp.height-1, disp.width-1)), outline="yellow")
	stwrite3("[ Gönnen Sie sich eine Pause - die Musiktitel kommen gleich! ]")

	station = STATIONS[stationnr]

	stationname =station[0]
	stationurl = station[1]

	try:
		stationselecttimer.cancel()
	except:
		pass

	if muted:
		startvolume = 0
	else:
		startvolume = 1.0*volumesteps[volstep]

	player.volume = startvolume
	logger.warning(f"playing station #{stationnr} ({stationname}) {stationurl}")
	player.play(stationurl)
	showvolume(draw)


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

def setvol(volstep, graceful, show=False):
	global volumetimer,disp,img,stationimg,volimg

	volimg = stationimg.copy()
	draw = ImageDraw.Draw(volimg)
	showvolume(draw)
	if show:
		disp.display(volimg)

	volume = volumesteps[volstep]

	try:
		volumetimer.cancel()

	except:
		pass

	if (graceful):

		volumetimer = Timer( 0.2, sendvolume, args=( volume, ) )
		volumetimer.start()

	else:
		sendvolume( volume )


def playstation(stationnr, graceful=True):
    global stationselecttimer,draw,disp,img

    try:
        stationselecttimer.cancel()
    except:
        pass

    station = STATIONS[stationnr]

    cleardisplay()
    draw.rectangle( ((0, 0, disp.width-1, disp.height-1)), outline="yellow")

#    draw.rectangle((1, 1, disp.width-2, 31), fill=(0, 0, 0, 0))
    cursor = stwrite( (0,0), "{0}".format( stationcounter+1 ), stationfont, "red" )
    cursor = stwrite( cursor, " {0}".format( station[0] ), stationfont, "white" )
    disp.display(img)

    if (graceful):

        stationselecttimer = Timer( graceperiod, stationplay, args=( stationnr, ) )
        stationselecttimer.start()

    else:

        stationplay( stationnr )


def updstationcounter(stationcounter):
	global cfgdata

	cfgdata['station']=stationcounter
	with open(cfgfile, "w") as outfile:
		json.dump(cfgdata, outfile, indent=4)

def updmuted():
	global cfgdata,muted

	muted=player.mute
	cfgdata['muted']=muted
	logger.warning(f"muted: {muted}")
	with open(cfgfile, "w") as outfile:
		json.dump(cfgdata, outfile, indent=4)

def updvol(volstep):
	global cfgdata

	cfgdata['volstep']=volstep
	with open(cfgfile, "w") as outfile:
		json.dump(cfgdata, outfile, indent=4)


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

def handle_stationincrement_button(pin, level, tick):
	global stationcounter

	buttonpressed(pin)
	displaywasoff = triggerdisplay()

	if muted:
		player.mute = False
		updmuted()
		showicytitle()
		setvol(volstep, graceful=False, show=True)

	if displaywasoff:
		return

	stationcounter = (stationcounter+1) % len(STATIONS)
	updstationcounter(stationcounter)
	playstation(stationcounter, graceful=True)


def handle_stationdecrement_button(pin, level, tick):
	global stationcounter

	buttonpressed(pin)
	displaywasoff = triggerdisplay()

	if muted:
		player.mute = False
		updmuted()
		showicytitle()
		setvol(volstep, graceful=False, show=True)

	if displaywasoff:
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

	draw.text( ( 120, 70 ),
		"{0}\n{3}\n{1}\n{2}\n{4}\n{5} dB".
		format(hostname,githash[0],githash[1],ipaddr,ssid,rssi),
		font=font20, fill="white", anchor="mm" )

	draw.text( ( 120, 160 ),
		"{0}".format(timenow()), font=font46, fill="white", anchor="mm" )
	showvolume(draw,"white","black")
	disp.display(timeimg)

	retriggerbacklight(timeout=timeout)

	if not is_showtimeOn or force:
		showtimetimer = Timer( timeout+1.0, showcurrentimg, args=() )
		showtimetimer.start()


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

	retriggerbacklight(dutycycle=100,timeout=120)

	logger.warning("code5656 detected")
	soundplayer.wait_for_playback() # wait finishing previous beep

	stwrite3("restarting the WiFi")
	beepwait()

	logger.warning("muting player and soundplayer")

	player.mute=True

	os.system('sudo ifdown --force wlan0')
	time.sleep(1)

	os.system('sudo ifup wlan0')
	# os.system('wpa_cli -i wlan0 reconfigure')

	time.sleep(1)

	# wait for network coming back
	hostname,ipaddr,ssid,rssi = get_networkinfo()
	stwrite3(ipaddr)

	logger.warning("unmuting player and soundplayer")
	restartplayer()
	player.mute=False
	updmuted()

	beep()

def showicytitle():
	md = player.metadata
	if md is not None and 'icy-title' in md:

		stwrite3(md['icy-title'])

def teatimerready():
	quindar1wait()
	logger.warning("Teatimer has expired")
	stwrite3("Teatimer 2:30 has expired")
	triggerdisplay()

	lastvol=player.volume
	player.volume=0.5*lastvol
	servicebellwait(volumepercent=200)
	servicebellwait(volumepercent=200)
	servicebellwait(volumepercent=200)
	playsound(volumepercent=200, soundfile="/home/pi/sounds/teetimer-abgelaufen.mp3")
	player.volume=lastvol
	quindar2()

def dummycb(pin=None,level=None,tick=None):
	return

def special_station0(pin=None,level=None,tick=None):
	global stationcounter

	buttonqueue.clear()
	logger.warning("Button X+B detected: tuning to station 1")

	displaywasoff = triggerdisplay()

	if muted:
		player.mute = False
		updmuted()
		showicytitle()
		setvol(volstep, graceful=False, show=True)

	if displaywasoff:
		return

	stationcounter = 0
	updstationcounter(stationcounter)
	playstation(stationcounter, graceful=True)


def special_teatimer(pin=None,level=None,tick=None):
	quindar1()
	buttonqueue.clear()

	teatimer = Timer( 180, teatimerready )
	teatimer.start()

	logger.warning("Teatimer started")
	stwrite3("Starting Teatimer 2:30")
	triggerdisplay()

	lastvol=player.volume
	player.volume=0.5*lastvol
	playsound(volumepercent=200, soundfile="/home/pi/sounds/teetimer-2min30.mp3")
	player.volume=lastvol
	quindar2()

def special_restartplayer(pin=None,level=None,tick=None):
	quindar1()
	buttonqueue.clear()
	logger.warning("code 5656 or A+X detected: restarting player")

	stwrite3("restarting the player")
	quindar2()

	restartplayer()

def special_shutdown(pin=None,level=None,tick=None):
	quindar1()
	buttonqueue.clear()
	logger.warning("code X+Y deteced: gracefully shutting down")

	stwrite3("shutting down")
	quindar2()

	killer.killed = True
	killer.shutdown = True

def special_updatecode(pin=None,level=None,tick=None):
	quindar1()
	buttonqueue.clear()
	logger.warning("code 6565 detected: updating code")

	stwrite3("updating the code")
	quindar2()

	os.system("cd /home/pi && git pull && sudo reboot now")

def special_mute(pin=None,level=None,tick=None):
	player.mute = True
	updmuted()

	img = Image.new('RGB', (disp.width, disp.height), color="blue")
	draw = ImageDraw.Draw(img)

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)

	draw.text( ( 120, 80),
		"muted", font=font, fill="white", anchor="mm" )

	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 46)
	draw.text( ( 120, 160 ),
		"{0}".format(timenow()), font=font, fill="white", anchor="mm" )

	disp.display(img)

	servicebell(100)
	triggerdisplay(timeout=10)


def buttonpressed(pin):
	global anybuttonpressed,bptimer,buttonqueue

	beep(volumepercent=50)
	blinkled(1)
	anybuttonpressed = True
	buttonqueue.append(pin)

	if seqmatch(code5656,buttonqueue):
		buttonqueue.clear()
		restartWifi()
		return

	if seqmatch(code6565,buttonqueue):
		# special_restartplayer()
		special_updatecode()
		return

	if seqmatch(code55555566,buttonqueue):
		buttonqueue.clear()
		player.play(minimal4)
		player.loop_file="inf"
		cleardisplay()
		stwrite3(minimal4)
		return

	if seqmatch(code5555566,buttonqueue):
		buttonqueue.clear()
		player.play(minimal3)
		player.loop_file="inf"
		cleardisplay()
		stwrite3(minimal3)
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

def handle_volumeincrement_button(pin, level, tick):
	global volstep

	buttonpressed(pin)
	displaywason = triggerdisplay()

	if muted:
		player.mute = False
		updmuted()
		showicytitle()
		setvol(volstep, graceful=False, show=True)
		triggerdisplay()
		if not volumebutton_after_mute_direct:
			return
	elif displaywason:
			return

	if volstep < len(volumesteps)-1:
		volstep += 1
		updvol(volstep)
		setvol(volstep, graceful=False, show=True)

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

def handle_volumedecrement_button(pin, level, tick):
	global volstep,grace,volumedecrementbuttonblock,buttonqueue

	buttonpressed(pin)

	if volumedecrementbuttonblock:
		return
	blockvolumedecrementbutton()

	displaywason = triggerdisplay()

	if muted:
		player.mute = False
		updmuted()
		showicytitle()
		setvol(volatep, graceful=False, show=True)
		triggerdisplay()
		if not volumebutton_after_mute_direct:
			return

	starttime = time.time()

#	while GPIO.input(pin) == 0 and time.time()-starttime < 1:
#		time.sleep(0.2)

	time.sleep(0.2) # debounce
	while pi.read(pin) == 0 and time.time()-starttime < 1:
		time.sleep(0.2)

	if time.time()-starttime >= 1:

		if muted:

			player.mute = False
			updmuted()
			showicytitle()
			triggerdisplay()
			if not volumebutton_after_mute_direct:
				return

		else:

			special_mute()

			while pi.read(pin) == 0 and time.time()-starttime < 5:
				time.sleep(0.2)

			if time.time()-starttime > 5:

				cleardisplay()
				triggerdisplay()

				killer.killed = True
				killer.shutdown = True

			else:

				time.sleep(10-time.time()+starttime)
				showtime(timeout=10,force=True)
				buttonqueue.clear()
				return

	else:
		triggerdisplay()

		if volstep > 0:
			volstep -= 1
			updvol(volstep)
			setvol(volstep, graceful=False, show=True)

def cb(gpio, level, tick):
	print(gpio, level, tick)
	for i in range(100):
		print(pi.read(gpio),end="")
		sleep(0.001)
	print()


def setup_button_handlers():

	# Loop through out buttons and attach the "handle_button" function to each
	# We're watching the "FALLING" edge (transition from 3.3V to Ground) and
	# picking a generous bouncetime of 100ms to smooth out button presses.

	for pin in BUTTONS:
		pi.set_pull_up_down(pin, pigpio.PUD_UP)
		pi.set_mode(pin, pigpio.INPUT)
		pi.set_glitch_filter(pin, steady)

	# pi.callback( PIN['Y'], pigpio.FALLING_EDGE, handle_stationincrement_button)
	# pi.callback( PIN['X'], pigpio.FALLING_EDGE, handle_stationdecrement_button)
	# pi.callback( PIN['B'], pigpio.FALLING_EDGE, handle_volumeincrement_button)
	# pi.callback( PIN['A'], pigpio.FALLING_EDGE, handle_volumedecrement_button)

	TwoButtons(PIN['X'],PIN['A'],PIN['Y'],PIN['B'],
		handle_stationdecrement_button, #1
		handle_volumedecrement_button, #2
		handle_stationincrement_button, #3
		handle_volumeincrement_button, #4
		special_restartplayer, #12
		special_shutdown, #13
		special_station0, #14
		special_station0, #23
		special_mute, #24
		special_teatimer) #34

def restartplayer():
	logger.warning(" ")
	logger.warning("*** restarting player")
	stationplay( stationcounter )


def shutdown():

	servicebellwait(100)
	beep3()
	setbacklight(100)

	img = Image.new('RGB', (disp.width, disp.height), color="red")
	draw = ImageDraw.Draw(img)
	font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
	draw.text( ( 120, 120), "Good\nbye", font=font, fill="white", anchor="mm" )
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
	cleardisplay()
	disp.display(img)

	player.quit()
	soundplayer.quit()

	if killer.shutdown:
		logger.warning("*** sudo shutdown -h now")
		print("Shutdown")
		os.system("sudo shutdown -h now")
	else:
		logger.warning("*** program gracefully terminated")
		logger.warning(" ")
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

		# print(f'{player_name}: {prop_val}')

		try:
			icyinfo = prop_val['icy-title']
			# logger.warning(f"icyinfo: {icyinfo}")

			# Test
			# correct max font_size = 28
			# icyinfo="Erdbeben-Hilfe mit Hindernissen: Enttäuschung bei Türken und Kurden in Berlin, Luise Sammann"
			# The optimum font size determination fails for:
			# icyinfo="Brahms, Fiala und Dvorak mit dem Tschechischen Philharmonischen Chor Brno, R. Kruzik/Martinu-Philharmonie/Fialova/Sibera/Barak"

			stwrite3(icyinfo)
			if not muted:
				retriggerbacklight(dutycycle=100,timeout=icyBacklightTimeout)

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
		logger.warning(f"-- autoplay; tuning to station #{newsstationcount}")
		playstation(newsstationcount, graceful=False)

		# resume playing the previous station (stationcounter)
		# in n seconds
		timer_resumeplay = Timer( 5*60, resumeplay, args=( stationcounter, newsstationcount ) )
		timer_resumeplay.start()
	else:
		logger.warning(f"-- autoplay: nothing to do, station #{newsstationcount} is already playing")

def resumeplay(laststation, newsstationcount):
	global stationcounter

	# switch to the currently selected station
	# except when the user selected the newsstation when this was played
	# In this case, a station change is not needed

	if stationcounter != newsstationcount:
		playstation(stationcounter, graceful=False)
		logger.warning(f"-- resume from autoplay: tuning back to station #{stationcounter}")
	else:
		logger.warning(f"-- resume from autoplay: nothing to do, station #{stationcounter} is already playing")

def mutecheck():
	if muted:
		blinkled(2)
	else:
		blinkled(1)

def threadedBlinkledFunction(n=1):
	for i in range(n):
		pi.write(ACT, 0) # on
		time.sleep(0.03)
		pi.write(ACT, 1) # off
		time.sleep(0.3)

def blinkled(n=1):
	t = Thread( target=threadedBlinkledFunction, daemon=True, args=( n, ) )
	t.start()


def setup_scheduler():
	newsstation = 0
	schedule_playnews = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_playnews.add_job(playnews, 'cron', minute=0, args=( newsstation, ) )

#	https://apscheduler.readthedocs.io/en/stable/modules/triggers/cron.html
#	https://apscheduler.readthedocs.io/en/stable/modules/triggers/date.html
#
#	Example for a certain time/date
#	schedule_playnews.add_job(playnews, 'date', run_date=datetime(2023, 03, 25, 20, 0, 0), args=( 0, ) )

	schedule_playnews.start()

	schedule_showtime = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_showtime.add_job(mutecheck, 'cron', second="*/5")
	schedule_showtime.start()

	schedule_showtime = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_showtime.add_job(blinkled, 'cron', minute="*")
	schedule_showtime.start()

	schedule_gong1 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong1.add_job(gong1, 'cron', minute=15)
#	schedule_gong1.start()

	schedule_gong2 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong2.add_job(gong2, 'cron', minute=30)
#	schedule_gong2.start()

	schedule_gong3 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong3.add_job(gong3, 'cron', minute=45)
#	schedule_gong3.start()

	schedule_gong4 = BackgroundScheduler(daemon=True,timezone=str(tzlocal.get_localzone()))
	schedule_gong4.add_job(gong4, 'cron', minute=0)
	schedule_gong4.start()

if __name__ == '__main__':

	import logging
	import mylogger
	logger = mylogger.setup( "WARNING", "/tmp/pinetradio.log" )

	# set mpv options to use the *mixing* alsa channel

	# https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=898575
	# https://medium.com/intrasonics/robust-continuous-audio-recording-c1948895bb49
	# https://wiki.ubuntuusers.de/mpv/

	# Remark:
	# 'stream_lavf_o' : 'reconnect_streamed=1,reconnect_delay_max=300,reconnect_at_eof=1',
	# does not work with playlist urls/files such as http://somafm.com/seventies.pls

	options1= {
		'audio_device' : 'alsa/plugmixequal',
		'volume_max' : '1000.0',
		'keep_open' : 'no',
		'idle' : 'yes',
		'gapless_audio' : 'weak',
#		'audio_buffer' : '0.2',
		'audio_buffer' : '1.0',
		'network_timeout' : '60',
		'stream_lavf_o' : 'reconnect_streamed=1,reconnect_delay_max=300',
		'cache-secs' : '5',
		'demuxer_thread' : 'yes',
		'demuxer_readahead_secs' : '5',
		'demuxer_max_bytes' : '2MiB',
		'load_unsafe_playlists' : 'yes'
	}

	player = mpv.MPV( **options1 )
	# player.audio_buffer = 3.0

# loss-of-stream:
# Vermutlich bekommst du in diesem Fall ein "MpvEventEndFile"
# mit gesetzem "Error"-Feld:
# https://github.com/jaseg/python-mpv/blob/main/mpv.py#L443
#
# Teste das doch mal mit einem Event-Callback, das einfach die Events logged, z.B.:
# ... und schaue, was das auf der Konsole ausgibt.

	@player.event_callback('end-file')
	def print_event(evt):

		# Event: {'event_id': 7, 'error': 0, 'reply_userdata': 0, 'event': {'reason': 2, 'error': 0}}
		if (evt['event']['reason'] != 2) or (evt['event']['error'] != 0):
			logger.warning(f"*** Event: {evt}")

		# restartplayer()

# Falls du später nicht mit Callbacks arbeiten möchtest,
# kannst du auch synchron auf so ein Event warten:
# player.wait_for_event('end-file', cond=lambda evt: evt.reason == MpvEventEndFile.ERROR)

	options2= {
		'audio_device' : 'alsa/plugmixequal',
		'volume_max' : '1000.0',
		'keep_open' : 'no',
		'idle' : 'yes',
		'gapless_audio' : 'no',
		'audio_buffer' : '0.0',
		'cache' : 'no',
		'demuxer_thread' : 'no'
	}


	soundplayer = mpv.MPV( **options2 )

	servicebell()

	setupdisplay()
	setup_button_handlers()

	killer = GracefulKiller()
	kill_processes()

	playstation(stationcounter, graceful=False)

	player.observe_property('metadata', make_observer('player'))
	# remark: player.metadata would get the metadata upon request

	logger.warning(f"mpv streamplayer options1: {options1}")
	logger.warning(f"mpv soundplayer options2: {options2}")
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
