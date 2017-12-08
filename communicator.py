import com_reader
import serial
from serial.tools import list_ports

class communicator(object):
	"""	communicator handles all external comunication with comports, server/s or p2p....
		...
	"""
	def __init__(self, arg):
		super(communicator, self).__init__()
		self.arg = arg
		self.threadq=queue.Queue()
		self.comstream
		self.readerthread

	def startcommunication(self):
		self.readerthread.run()

	def connect(self,,arg):
		try:
			# if port is open, close it
			if self.comstream.is_open:
				self.comstream.close()

			# kill thread if it's alive 
			if self.readerthread.isAlive():
				self.readerthread.stop(0.01)

			#if arg.local:
			self.comstream=serial()	#change to local com... init
			self.comstream.baudrate=arg.baudrate
			self.comstream.port=arg.port
			self.comstream.timeout=arg.timeout
			#else:
				#if arg.server
					#self.comstream=	#server init...
				#else:
					#self.comstream=	#p2p??? init...
			self.readerthread=com_reader.ComReaderThread(self.comstream,self.threadq)
		except Exception as e:




	def getPorts(self):
		# lists all the available devices connected to the computer
		port_list = list_ports.comports()
		ports = [port.device for port in port_list]

		ports.append('Custom')
		return sorted(ports)


	