import mpv
import signal
import time
from datetime import datetime

def now():
        currentDateAndTime = datetime.now()
        return currentDateAndTime.strftime("%Y%m%d%H%M%S")

def make_observer(player_name):
	def observer(_prop_name, prop_val):
		# print(f'{player_name}: {prop_val}')

		try:
			title = prop_val['icy-title']
			print( now() + " " + title )
		except:
			pass

	return observer


# using alsa + dmixer + equalizer
# see .asoundrc

options= { 	'audio_device':'alsa/plugmixequal',
		'volume_max':'1000.0' }

player = mpv.MPV( **options )

player.observe_property('metadata', make_observer('player'))
player.volume=10.0

# Play a stream from the internet (SomaFm Groove Salad)
player.play('http://ice1.somafm.com/groovesalad-128-mp3')

time.sleep(5)

# Play a sound file from the local filesystem
player2.play('/home/pi/beep.wav')

signal.pause()
