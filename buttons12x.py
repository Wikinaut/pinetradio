#!/usr/bin/env python3
import signal
import pigpio
import time
from threading import Timer

print("""buttons12.py - Detect which button has been pressed

This example should demonstrate how to:
1. set up pigpio to read buttons
2. determine which button has been pressed
3. test two-button clicks

Press Ctrl+C to exit!

""")

pi = pigpio.pi()	   # pi accesses the local Pi's GPIO

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


	def callbackTwo(self,both):

		if both != self.last:

			self.last = both
			clrlastTimer = Timer( 0.1, self.clrlast_cb, args=() )
			clrlastTimer.start()

			if both == "12":
				self.callback12()
			elif both == "13":
				self.callback13()
			elif both == "14":
				self.callback14()
			elif both == "23":
				self.callback23()
			elif both == "24":
				self.callback24()
			elif both == "34":
				self.callback34()


	# common button press callback for both buttons
	def button_pressed(self, pin, button, tick):

		both = None

		if pin == self.button1:

			if button == pressed:

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
						self.callback1()
					if self.pi.read(self.button2) == pressed:
						self.callback2()
					if self.pi.read(self.button3) == pressed:
						self.callback3()
					if self.pi.read(self.button4) == pressed:
						self.callback4()

				if both:
					self.callbackTwo(both)

		elif pin == self.button2:

			if button == pressed:

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
						self.callback1()
					if self.pi.read(self.button2) == pressed:
						self.callback2()
					if self.pi.read(self.button3) == pressed:
						self.callback3()
					if self.pi.read(self.button4) == pressed:
						self.callback4()

				if both:
					self.callbackTwo(both)

		elif pin == self.button3:

			if button == pressed:

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
						self.callback1()
					if self.pi.read(self.button2) == pressed:
						self.callback2()
					if self.pi.read(self.button3) == pressed:
						self.callback3()
					if self.pi.read(self.button4) == pressed:
						self.callback4()

				if both:
					self.callbackTwo(both)

		elif pin == self.button4:

			if button == pressed:

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
						self.callback1()
					if self.pi.read(self.button2) == pressed:
						self.callback2()
					if self.pi.read(self.button3) == pressed:
						self.callback3()
					if self.pi.read(self.button4) == pressed:
						self.callback4()

				if both:
					self.callbackTwo(both)


def cb1():
	print("button 1 cb")

def cb2():
	print("button 2 cb")

def cb3():
	print("button 3 cb")

def cb4():
	print("button 4 cb")

def cb12():
	print("button 12 cb")

def cb13():
	print("button 13 cb")

def cb14():
	print("button 14 cb")

def cb23():
	print("button 23 cb")

def cb24():
	print("button 24 cb")

def cb34():
	print("button 34 cb")

TwoButtons(5,6,16,24,cb1,cb2,cb3,cb4,cb12,cb13,cb14,cb23,cb24,cb34)

while True:
	# keep the program alive
	signal.pause()
