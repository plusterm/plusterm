from wx.lib.pubsub import pub
import serial
import threading
import queue
import time
import datetime


class ComReaderThread(threading.Thread):
	''' 
	Creates a thread that continously reads from the serial connection
	Puts result as a tuple (timestamp, data) in a queue
	'''
	
	def __init__(self, ser, data_que, error_que):
		threading.Thread.__init__(self)
		self.comstream = ser
		self.data_que = data_que
		self.error_que = error_que

		self.alive = threading.Event()
		self.alive.set()


	def run(self):

		# start the timer
		startTime = time.time()	#	start "timer"

		while self.alive.isSet():
			try:
				# reads data until newline (x0A/10) 
				data = self.comstream.read()
				if len(data) > 0:

					timestamp = time.time() - startTime
					#timestamp = datetime.datetime.now()

					while data[-1] != 0x0A:
						data += self.comstream.read()

					self.data_que.put((timestamp, data))
					
			except serial.SerialException as e:
				reconnected=False
				print('Serial connection lost, trying to reconnect.')
				ts = time.time()
				self.error_que.put((ts, str(e)))
				while not reconnected:
					try:
						#	if comstream still thinks it's open close it
						if self.comstream.is_open:
							self.comstream.close()
						
						self.comstream.open()
						
					except Exception as e:	
						# if reconnection failed let some time pass					
						time.sleep(0.1)

					else:
						reconnected=True	
						print('Reconnected')			


	def stop(self, timeout=None):		
		self.alive.clear()
		threading.Thread.join(self, timeout)
