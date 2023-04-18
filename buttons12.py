import signal
import pigpio
import time

pi = pigpio.pi()	   # pi accesses the local Pi's GPIO

print("""buttons12.py - Detect which button has been pressed

This example should demonstrate how to:
1. set up pigpio to read buttons
2. determine which button has been pressed
3. test two-button clicks

Press Ctrl+C to exit!

""")

# The buttons on Pirate Audio are connected to pins 5, 6, 16 and 24
# Boards prior to 23 January 2020 used 5, 6, 16 and 20
# try changing 24 to 20 if your Y button doesn't work.
BUTTONS = [5, 6, 16, 24]

# These correspond to buttons A, B, X and Y respectively
LABELS = ['A', 'B', 'X', 'Y']

steady = 20000 # microseconds

# https://forums.raspberrypi.com/viewtopic.php?t=238131
# remember to start pigpio - sudo pigpiod

pressed = pigpio.LOW
released = pigpio.HIGH


class TwoButtons():

	def __init__(self,button1,button2):

		# get a pigpio instance
		self.pi = pigpio.pi()

		# set up buttons
		self.button1 = button1
		self.button2 = button2

		# set up glitch filter to debounce each switch
		self.pi.set_glitch_filter(self.button1, steady)
		self.pi.set_glitch_filter(self.button2, steady)

		# set up each button as an input
		self.pi.set_mode(self.button1, pigpio.INPUT)
		self.pi.set_mode(self.button2, pigpio.INPUT)

		# create a callback for when button is pressed
		self.pi.callback(self.button1, pigpio.EITHER_EDGE, self.button_pressed)
		self.pi.callback(self.button2, pigpio.EITHER_EDGE, self.button_pressed)


	# common button press callback for both buttons
	def button_pressed(self, pin, button, tick):

		both = False

		if button == pressed:
			# print()
			# label = LABELS[BUTTONS.index(pin)]
			# print('pin: {} label: {} value:{}'.format(pin, label, value))
			# print(label)
			pass

		# button 1 state changed
		if pin == self.button1:

			if button == pressed:

				for _ in range(10):
					if self.pi.read(self.button2) == pressed:
						# print("both buttons pressed")
						both = True
						break
					time.sleep(0.005)

				if not both and self.pi.read(self.button1) == pressed:
					# print("button 1 (clean)")
					callback1()

			else:
			# elif button == released:

				if self.pi.read(self.button2) == pressed:
					# print("button 2 still pressed")
					pass
				else:
					# print("both buttons released")
					pass

		elif pin == self.button2:

			if button == pressed:

				for _ in range(10):
					if self.pi.read(self.button1) == pressed:
						# print("both buttons pressed")
						both = True
						break
					time.sleep(0.005)

				if not both and self.pi.read(self.button2) == pressed:
					# print("button 2 (clean)")
					callback2()

			else:
			# elif button == released:

				if self.pi.read(self.button1) == pressed:
					# print("button 1 still pressed")
					pass
				else:
					# print("both buttons released")
					pass

			if both:
				# print("both buttons pressed")
				callback12()


def callback1():
	print("button 1 cb")

def callback2():
	print("button 2 cb")

def callback12():
	print("button 12 cb")

TwoButtons(5,16)

while True:
	# keep the program alive
	signal.pause()
