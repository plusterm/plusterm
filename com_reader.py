import serial
import threading
import queue
import time


class ComReaderThread(threading.Thread):
	''' 
	Creates a thread that continously reads from the serial connection
	Puts result as a tuple (timestamp, data) in a queue
	'''
	
	def __init__(self, ser, que):
		threading.Thread.__init__(self)
		self.ser = ser
		self.que = que

		self.alive = threading.Event()
		self.alive.set()

	def run(self):

		# start the timer
		startTime = time.time()

		while self.alive.isSet():
			try:
				# reads data until newline (x0A/10) 
				data = self.ser.read()
				if len(data) > 0:

					timestamp = time.time() - startTime

					while data[-1] != 0x0A:
						data += self.ser.read()

					self.que.put((timestamp, data))
			except serial.SerialException as e:
				print("reader:no connection!\n{}".format(e))
				self.ser.close()
				time.sleep(0.5)
				# pass


	def stop(self, timeout=None):		
		self.alive.clear()
		threading.Thread.join(self, timeout)