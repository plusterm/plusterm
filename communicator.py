import queue
import serial
import time
import re
from wx.lib.pubsub import pub
from serial.tools import list_ports
from com_reader import ComReaderThread

class Communicator():
	"""	communicator handles all external comunication with comports, server/s or p2p....
		etc...
	"""

	def __init__(self,context):
		self.threadq=queue.Queue()
		self.comstream=None
		self.readerthread=None
		self.context=context
		

	def start_communication(self):
		self.readerthread.run()


	def connect(self, **options):
		try:
			self.comstream = serial.Serial()
			self.comstream.port = options['port']
			self.comstream.baudrate = options['baudrate']
			self.comstream.timeout = 0.1
			
			self.comstream.open()
	
			if self.readerthread is not None:
				if not self.readerthread.isAlive():
					self.readerthread = ComReaderThread(self.comstream, self.threadq)
					self.readerthread.start()
	
			else:
				self.readerthread = ComReaderThread(self.comstream, self.threadq)
				self.readerthread.start()

			return True

		except Exception as e:
			print(e)
			return False

	
	def disconnect(self):
		"""	stops/close all threads and streams
		"""
		try:
			self.readerthread.stop(0.01)
			self.comstream.close()
			return True

		except:
			return False
			

	def send_cmd(self,cmd):
		"""	send a command to the comstream assuming it is a string
		"""
		if self.comstream is not None:
			self.comstream.write(cmd.encode())


	def get_data(self):
		"""	get the data from the readerthreadqueue
		"""
		return self.threadq.get(False)
	
	
def getPorts():
	# lists all the available serial devices connected to the computer
	port_list = list_ports.comports()
	ports = [port.device for port in port_list]
	return sorted(ports)


