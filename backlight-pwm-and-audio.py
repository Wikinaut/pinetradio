#!/usr/bin/env python

#	PWM backlight dim for ST7789 displays
#	for Raspberry Pi with Pirate Audio HAT (DAC)
#
#	The pigpio daemon must be run with -t 0 option
#	(unlike the default option),
#	because the PCM timer is used by the Pirate Audio HAT DAC.
#
# 	pigpiod -l -t 0
#	t value, clock peripheral, 0=PWM 1=PCM, default PCM
#
#	recommended /lib/systemd/system/pigpiod.service:
#
#	[Unit]
#	Description=Daemon required to control GPIO pins via pigpio
#	[Service]
#	ExecStart=/usr/bin/pigpiod -l -t 0
#	ExecStop=/bin/systemctl kill pigpiod
#	Type=forking
#	[Install]
#	WantedBy=multi-user.target

import time
import math
import pigpio
from ST7789 import ST7789
from PIL import Image, ImageDraw
import mpv


print("""backlight-pwm.py - Demonstrate the backlight being controlled by PWM

This advanced example shows you how to achieve a variable backlight
brightness using PWM.

Instead of providing a backlight pin to ST7789, we set it up using
pigpio's  PWM functionality with a fixed frequency and adjust the
duty cycle to change brightness.

Press Ctrl+C to exit!
""")

SPI_SPEED_MHZ = 90

# Give us an image buffer to draw into
image = Image.new("RGB", (240, 240), (255, 0, 255))
draw = ImageDraw.Draw(image)

# Standard display setup for Pirate Audio, except we omit the backlight pin
st7789 = ST7789(
    rotation=90,     # Needed to display the right way up on Pirate Audio
    port=0,          # SPI port
    cs=1,            # SPI port Chip-select channel
    dc=9,            # BCM pin used for data/command
    backlight=None,  # We'll control the backlight ourselves
    # backlight=13,  # 13 for Pirate-Audio; 18 for back BG slot, 19 for front BG slot.
    spi_speed_hz=SPI_SPEED_MHZ * 1000 * 1000
)


pi = pigpio.pi()       # pi accesses the local Pi's GPIO

# We must set the backlight pin up as an output first
pi.set_mode(13, pigpio.OUTPUT)

# Set up our pin as a PWM output at 1000Hz
pi.set_PWM_frequency(13, 1000)

# Start the PWM at 100% duty cycle (255)
pi.set_PWM_dutycycle(13, 255)


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

# define a player
player = mpv.MPV( **options )

# Play a stream from the internet (SomaFm Groove Salad)
player.volume=60.0

# player.play('http://somafm.com/seventies.pls')
player.play('http://ice1.somafm.com/groovesalad-128-mp3')


while True:
    # Using math.sin() we can convert the linear progression of time into
    # a sine wave, shift it up by +1 to eliminate the negative component
    # and divide by two to give us a range of 0.0 - 1.0 which we can then
    # multiply by 100 to get our duty cycle percentage.
    # Of course - this is purely for this demonstration and you'll likely
    # do something much simpler to pick your brightness!
    brightness = ((math.sin(time.time()) + 1) / 2.0) * 100
    pi.set_PWM_dutycycle(13, brightness*255/100)

    draw.rectangle((0, 0, 240, 240), (255, 0, 255))

    # Draw a handy on-screen bar to show us the current brightness
    bar_width = int((220 / 100.0) * brightness)
    draw.rectangle((10, 220, 10 + bar_width, 230), (255, 255, 255))

    # Display the resulting image
    st7789.display(image)
    time.sleep(1.0 / 30)

pi.stop()
