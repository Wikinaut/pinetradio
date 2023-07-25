# pinetradio
RaspberryPi Internetradio

* Raspberry Zero WH
* plus Pirate Audio Line-Out HAT with LCD-Display 240x240 pixel
  * Hardware: https://shop.pimoroni.com/products/pirate-audio-line-out  
  https://www.berrybase.de/pirate-audio-hat-fuer-raspberry-pi-line-out
  * Software:  
  `sudo apt install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy`  
  `sudo apt install pigpio python3-pigpio`  
  https://github.com/pimoroni/pirate-audio  
  ST7789 display driver https://github.com/pimoroni/st7789-python  
  `pip install st7789`
  * `sudo systemctl disable rsyslog` # disable logging
  * `sudo systemctl enable pigpiod` # make sure to have `pigpiod -t 0` in /lib/systemd/system/pigpiod.service
  * `sudo systemctl start pigpiod` # make sure to have `pigpiod -t 0` in /lib/systemd/system/pigpiod.service
  * `sudo raspi-config`: → Interface Options → enable `SPI` for the LCD-display and enable `I2C` for the DAC
  * `sudo nano /boot/config.txt`:
    ```
    dtoverlay=hifiberry-dac
    gpio=25=op,dh
    # You can also disable onboard audio if you're not going to use it.
    # This sometimes helps applications find the right audio device without extra prompting:
    dtparam=audio=off
    ```
    The DAC can be configured by adding dtoverlay=hifiberry-dac to the /boot/config.txt file.  
    There is a DAC enable pin—BCM 25— that must be driven high to enable the DAC. You can do this by adding gpio=25=op,dh to the /boot/config.txt file.  
    The buttons are active low, and connected to pins BCM 5, 6, 16, and 24.  
    The display uses SPI, and you'll need to enable SPI through the Raspberry Pi configuration menu.  
    If you want to use these boards with a Pibow Coupé case (either for the Zero / Zero W or Pi 4), then you'll need to use a booster header to raise it up a little.  
    https://shop.pimoroni.com/products/pirate-audio-line-out
* Audio output using `mpv` engine
  * libmpv-dev
  * [python3-mpv](https://github.com/jaseg/python-mpv) library wrapper  
  ` sudo apt install mpv libmpv-dev python3-mpv `

#### Implemented features
- [x] advanced Icy-Title rendering:  
  trying to display the title with maximum font size and [hyphenation in Python](https://github.com/Kozea/Pyphen) on the 240x240 pixel display  
  `pip install pyphen`
- [x] medium long (< 3 seconds) volume-decrement-button press → mute
- [x] long ( > 3 seconds) volume-decrement-button press → controlled shutdown
- [x] time display every minute
- [x] display of basic network connection info (hostname, IP, SSID, signal strength)
- [x] key press signalling with beeps
- [x] `code`: certain hard-coded key press sequences (à la [port knocking](https://en.wikipedia.org/wiki/Port_knocking)) can trigger special actions or change certain program settings.  
  Example: the key sequence `A B A B` → restarts the WiFi adapter and networking; this takes about 2 seconds.
- [x] WiFi and networking can be manually restarted by a special key sequence (`code ABAB`)
- [x] display of basic network information (SSID, IP address, hostname and RSSI/signal strength)
- [x] ALSA: configured for multi-channel use with `dmix` plugin and equaliser plugin. `pinetradio` sends its one (stream) or two (beeps etc.) audio signals via `alsa/plugmixequal` to the dmixer which mixed signal is finally equalised, see `.asoundrc` for details and setup.  
`sudo apt install libasound2-plugin-equal`
- [x] `chime`: 1, 2, 3, 4 beeps at every hourly quarter (using `apscheduler`: `pip install apscheduler`)
- [x] Activity (ACT) LED indicates "on" (1x flash) or "muted" (2x flash ) every 5 seconds
- [X] Soundbox/Sound machine function: play stored sound files 
- [x] `cronplay` (`autoplay`): a station-play-scheduler for autoplaying certain station/s at certain times similar to `cron`  
Example: switch from the currently played first station to a certain second (e.g. news) station every hour minutes 00…05 and then switch back to the first station.
- [X] permanently show current network strength rssi (value in dB)
- [x] "kitchen" timer function (a few set of preprogrammed countdown timers for green tea etc.)
- [x] text-to-speech: informational messages with synthetic speech like station name, time and timer announcements 
- [x] controlling the onboard ACT LED for signalling purposes

#### TODO / Brain storming section

- [ ] add two rotary encoders for station / volume control
- [ ] Enable/disable `cronplay` with another special `code`.
- [ ] permanently show current network strength rssi (as a bar)
- [ ] reboot if rssi is too low
- [ ] check whether stream/mpv is still alive; watchdog; restart mpv.play()
- [ ] add a quick `record` function with or without a timeout: basically, this is as easy as only adding or removing on-the-fly `player.stream_record="filename"`
- [ ] `record` if certain Icy texts are detected: basically, it is only adding & removing `player.stream_record="filename"`
- [ ] playing randomly selected "Wurfsendungen" (Kurzhörspiele; short audio drama) at random times or as a random play list continuously.
- [ ] ALSA Equalizer: interface to show and control the equalizer settings
- [ ] add loudness on/off
- [ ] alarm clock function with sound and/or internet radio stream, increasing volume

#### special requirements

ST7789 library

![IMG_20230725_135840](https://github.com/Wikinaut/pinetradio/assets/1151915/f162a05a-f5a4-4932-a170-3500a65d41fc)
![IMG_20230725_140013](https://github.com/Wikinaut/pinetradio/assets/1151915/fdb11677-6a03-4492-b4d7-7b9d8328f64d)
![IMG_20230725_135914](https://github.com/Wikinaut/pinetradio/assets/1151915/730eeee9-a4cc-49a8-bcdc-015435f6a621)
![IMG_20230725_135825](https://github.com/Wikinaut/pinetradio/assets/1151915/8f711843-cfd5-4fad-94f0-c7d036789f70)

Example for Soundbox function (play stored sound/s):
![IMG_20230725_140200](https://github.com/Wikinaut/pinetradio/assets/1151915/6af0ea34-13c1-4ac0-b091-0662c8553f7e)

![IMG_20230725_140310](https://github.com/Wikinaut/pinetradio/assets/1151915/8a286525-d7e0-4c76-8f6e-d9183f5519eb)
![IMG_20230725_140320_pyxelate](https://github.com/Wikinaut/pinetradio/assets/1151915/3da61a90-ce56-4991-970f-830c2e808682)
