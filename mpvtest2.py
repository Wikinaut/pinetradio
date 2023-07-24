#!/usr/bin/env python3

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

# set mpv options to use the *mixing* alsa channel
# https://medium.com/intrasonics/robust-continuous-audio-recording-c1948895bb49
# https://wiki.ubuntuusers.de/mpv/

options= {
                'audio_device' : 'alsa/plugmixequal',
                'volume_max' : '1000.0',
                'keep_open' : 'no',
                'idle' : 'yes',
                'gapless_audio' : 'yes',
                'audio_buffer' : '0.2',
                'stream_lavf_o' : 'reconnect_streamed=1,reconnect_delay_max=300',
		'network_timeout' : '60',
		'cache-secs' : '2'
}

# define a first player
player = mpv.MPV( **options )
player.observe_property('metadata', make_observer('player'))

# Play a stream from the internet (SomaFm Groove Salad)
player.volume=60.0

# player.play('http://somafm.com/seventies.pls')
player.play('http://ice1.somafm.com/groovesalad-128-mp3')


# loss-of-stream:
# Vermutlich bekommst du in diesem Fall ein "MpvEventEndFile"
# mit gesetzem "Error"-Feld:
# https://github.com/jaseg/python-mpv/blob/main/mpv.py#L443
#
# Teste das doch mal mit einem Event-Callback, das einfach die Events logged, z.B.:
# ... und schaue, was das auf der Konsole ausgibt.

@player.event_callback('end-file')
def print_event(evt):
    print(evt)


# Falls du später nicht mit Callbacks arbeiten möchtest,
# kannst du auch synchron auf so ein Event warten:
# player.wait_for_event('end-file', cond=lambda evt: evt.reason == MpvEventEndFile.ERROR)

while True:
	md=player.metadata

	if md is not None and 'icy-title' in md:
		print(md['icy-title'])

	time.sleep(1)

# signal.pause()
