import serial
import threading
import queue
import time


class ComReaderThread(threading.Thread):
	''' 
	Creates a thread that continously reads from the serial connection
	Puts the result in a queue.

	Input: a serial connection, and a queue instance
	Output: tuple (timestamp, data) into queue
	'''
	
	def __init__(self, ser, que):
		threading.Thread.__init__(self)
		self.ser = ser
		self.que = que

		self.alive = threading.Event()
		self.alive.set()

	def run(self):

		# reset the timer
		startTime = time.clock()

		while self.alive.isSet():

			# reads data until newline (x0A/10) 
			data = self.ser.read(1)
			if len(data) > 0:
				while data[-1] != 0x0A:
					data += self.ser.read(1)

				timestamp = time.clock()
				self.que.put((timestamp, data))
			
		# close the connection when alive event is cleared
		if self.ser:
			self.ser.close()

	def stop(self, timeout=None):
		threading.Thread.join(self, timeout)
		self.alive.clear()