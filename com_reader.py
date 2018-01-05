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
		self.comstream = ser
		self.que = que

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

					while data[-1] != 0x0A:
						data += self.comstream.read()

					self.que.put((timestamp, data))
					
			except serial.SerialException as e:
				reconnected=False
				#log to gui?
				while not reconnected:
					try:
						#	if comstream still thinks it's open close it
						if self.comstream.is_open:
							self.comstream.close()
							
						#	do checks and setup connection again (will require acces to arg-structure)
						# if self.arg.local:
						# 	if not self.comstream.is_open:
						# 		self.comstream.baudrate=self.arg.baudrate
						# 		self.comstream.port=self.arg.port
						# 		self.comstream.timeout=self.arg.timeout
								# self.comstream.open()
						# 	else:
						# 		pass
						# else:	#	remote eg server or p2p etc
						# 	pass
						
						self.comstream.open()
						
					except Exception as e:	#	if reconnection failed let some time pass
						print('reconnector:{}\n'.format(e))
						time.sleep(0.1)
					else:
						reconnected=True
						#log to gui?
				


	def stop(self, timeout=None):		
		self.alive.clear()
		threading.Thread.join(self, timeout)
