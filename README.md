# pinetradio
RaspberryPi Internetradio

* Raspberry Zero WH
* plus Pirate Audio Line-Out HAT with LCD-Display 240x240 pixel
  * Hardware: https://shop.pimoroni.com/products/pirate-audio-line-out  
  https://www.berrybase.de/pirate-audio-hat-fuer-raspberry-pi-line-out
  * Software:  
  `sudo apt install python3-rpi.gpio python3-spidev python3-pip python3-pil python3-numpy`  
  https://github.com/pimoroni/pirate-audio  
  ST7789 display driver https://github.com/pimoroni/st7789-python  
  `pip install st7789`
  
* Audio output using `mpv` engine
  * libmpv-dev
  * [python3-mpv](https://github.com/jaseg/python-mpv) library wrapper  
  ` sudo apt install mpv libmpv-dev python3-mpv ` 
* advanced Icy-Title rendering:  
  trying to display the title with maximum font size and [hyphenation in Python](https://github.com/Kozea/Pyphen) on the 240x240 pixel display  
  `pip install pyphen`
* medium volume-decrement press: mute
* long volume-decrement press: controlled shutdown
* time display every minute
* display of basic network connection info (hostname, IP, SSID, signal strength)
* key press signalling with beeps
* `code`: coded key press sequences (à la [port knocking](https://en.wikipedia.org/wiki/Port_knocking)) for example `A, B, A ,B` → can trigger special actions or change certain program settings
* display of basic network information (SSID, IP address, hostname and RSSI/signal strength)
* ALSA: configured for multi-channel use with `dmix` plugin and equaliser plugin. `pinetradio` sends its one (stream) or two (beeps etc.) audio signals via `alsa/plugmixequal` to the dmixer which mixed signal is finally equalised, see `.asoundrc` for details and setup.  
`sudo apt install libasound2-plugin-equal`
* `chime`: 1, 2, 3, 4 beeps at every hourly quarter.

#### TODO / Brain storming section

* add two rotary encoders for station / volume control
* `cronplay`: a station-play-scheduler for autoplaying certain station/s at certain times similar to `cron`  
Example: switch from the currently played first station to a certain second (e.g. news) station every hour minutes 00…05 and then switch back to the first station. Enable/disable this function by a special `code`.
* permanently show current network strength rssi (bar + value)
* reboot if rssi is too low
* check whether stream/mpv is still alive; watchdog; restart mpv.play()
* add a quick `record` function with or without a timeout
* `record` if certain Icy texts are detected
* playing randomly selected "Wurfsendungen" (Kurzhörspiele; short audio drama) at random times or as a random play list continuously.

#### special requirements

ST7789 library

![grafik](https://user-images.githubusercontent.com/1151915/226862353-6494654d-b1ac-476f-9acd-1418b6f80afd.png)
![IMG_20230307_172928_edit_286222401319344](https://user-images.githubusercontent.com/1151915/223493327-ed8ce69a-5e18-4a8c-9d04-7432bc0ae5c0.jpg)
![IMG_20230307_172921_edit_286243996314132](https://user-images.githubusercontent.com/1151915/223493338-398a7b3f-69fc-477f-8bcc-537ab15db991.jpg)
![IMG_20230307_172842_edit_286413349799523](https://user-images.githubusercontent.com/1151915/223493342-0593e272-ae60-477d-ab75-160946dd4077.jpg)
