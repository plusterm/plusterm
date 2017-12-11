# import com_reader
import serial
from serial.tools import list_ports
from com_reader import ComReaderThread

class communicator():
	"""	communicator handles all external comunication with comports, server/s or p2p....
		etc...
		.
		.
		.
	"""
	def __init__(self, arg):
		#super(communicator, self).__init__()
		self.arg = arg
		self.threadq=queue.Queue()
		self.comstream=None
		self.readerthread=None

	def startcommunication(self):
		self.readerthread.run()

	def connect(self,,arg):
		try:
			# if port is open, close it
			if self.comstream != None:
				if self.comstream.is_open:
					self.comstream.close()

			# kill thread if it's alive 
			if self.readerthread !=None:
				if self.readerthread.isAlive():
					self.readerthread.stop(0.01)

			#if arg.local:
			self.comstream=serial()	#set to local com... init 
			self.comstream.baudrate=arg.baudrate
			self.comstream.port=arg.port
			self.comstream.timeout=arg.timeout
			self.comstream.open()

			#else:
				#if arg.server
					#self.comstream=	#server init...
				#else:
					#self.comstream=	#p2p??? init...
			self.readerthread=com_reader.ComReaderThread(self.comstream,self.threadq)
			self.readerthread.start()
			self.master.after(10,self,listenComThread)
			return True
		except Exception as e:
			#textoutput...
			return False



def getPorts():
	# lists all the available serial devices connected to the computer
	port_list = list_ports.comports()
	ports = [port.device for port in port_list]
	ports.append('Custom')
	return sorted(ports)


	