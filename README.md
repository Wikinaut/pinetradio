# pinetradio
RaspberryPi Internetradio

for 

* Raspberry Zero WH 
* plus Pirate Audio Line-Out HAT with LCD-Display 240x240 pixel
  * Hardware: https://shop.pimoroni.com/products/pirate-audio-line-out  
  https://www.berrybase.de/pirate-audio-hat-fuer-raspberry-pi-line-out
  * Software: https://github.com/pimoroni/pirate-audio
* using mpv engine
  * libmpv-dev
  * [python3-mpv](https://github.com/jaseg/python-mpv) library wrapper  
  ` sudo apt install mpv libmpv-dev python3-mpv ` 
* advanced Icy-Title rendering:  
  trying to display the title with maximum font size and hyphenation on the 240x240 pixel display
* medium volume-decrement press: mute
* long volume-decrement press: controlled shutdown
* time display every minute
* display of basic network connection info (hostname, IP, SSID, signal strength)
* key press signalling with beeps
* coded key press sequences (à la port knocking) for example `A, B, A ,B` → can trigger special actions or change setting
* display of basic network information (SSID, IP address, hostname and RSSI/signal strength)
* ALSA: configured for multi-channel use with `dmix` plugin and equaliser plugin. `pinetradio` send one or two audio signals via `alsa/plugmixequal` to the dmixer which mixed signal is finally equalised, see `.asoundrc` for details and setup.  
`sudo apt install libasound2-plugin-equal`


#### special requirements

ST7789 library
![IMG_20230307_172928_edit_286222401319344](https://user-images.githubusercontent.com/1151915/223493327-ed8ce69a-5e18-4a8c-9d04-7432bc0ae5c0.jpg)
![IMG_20230307_172921_edit_286243996314132](https://user-images.githubusercontent.com/1151915/223493338-398a7b3f-69fc-477f-8bcc-537ab15db991.jpg)
![IMG_20230307_172842_edit_286413349799523](https://user-images.githubusercontent.com/1151915/223493342-0593e272-ae60-477d-ab75-160946dd4077.jpg)
