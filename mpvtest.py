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
                'network_timeout' : '60',
                'stream_lavf_o' : 'reconnect_streamed=1,reconnect_delay_max=300,reconnect_at_eof=1',
		'cache-secs' : '5',
		'demuxer_thread' : 'yes',
		'demuxer_readahead_secs' : '5',
                'demuxer_max_bytes' : '2MiB'
}

# define a first player
player = mpv.MPV( **options )
player.observe_property('metadata', make_observer('player'))

# define a second player
player2 = mpv.MPV( **options )

# Play a stream from the internet (SomaFm Groove Salad)
player.volume=60.0

player.play('http://ice1.somafm.com/groovesalad-128-mp3')

time.sleep(5)

# Play a sound file from the local filesystem
player2.volume=60.0
player2.play('/home/pi/sounds/beep.wav')

signal.pause()
