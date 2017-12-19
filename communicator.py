# import com_reader
import serial
from serial.tools import list_ports
from com_reader import ComReaderThread
from reconnector import ReconnectorThread

class communicator():
	"""	communicator handles all external comunication with comports, server/s or p2p....
		etc...
		.
		.
		.
	"""
	def __init__(self,context,q):
		#super(communicator, self).__init__()
		
		self.threadq=q
		self.comstream=None
		self.readerthread=None
		self.context=context
		self.storedcomsetup=None
		self.reconnectorthread=None

	def startcommunication(self):
		self.readerthread.run()

	def connect(self,arg):
		try:
			doit=True
			if self.storedcomsetup is not None:
				if self.storedcomsetup.local!=arg.local or self.storedcomsetup.port!=arg.port or self.storedcomsetup.baudrate!=arg.baudrate:
					doit=True
				else:
					doit=False

			if doit:
				#	if reconector thread is open close it
				if self.reconnectorthread is not None:
					if self.reconnectorthread.isAlive():
						self.reconnectorthread.stop(0.01)

				# kill thread if it's alive 
				if self.readerthread is not None:
					if self.readerthread.isAlive():
						self.readerthread.stop(0.01)

				# if port is open, close it
				if self.comstream is not None:
					if self.comstream.is_open:
						self.comstream.close()

				

				if arg.local:
					self.comstream=serial.Serial()	#set to local com... init 
					self.comstream.baudrate=arg.baudrate
					self.comstream.port=arg.port
					self.comstream.timeout=arg.timeout
					self.comstream.open()

				else:
					pass
					#if arg.server
						#self.comstream=	#server init...
					#else:
						#self.comstream=	#p2p??? init...
			
			
					
			if not self.comstream.is_open:
				self.comstream.open()
				self.context.logoutputtogui('port opened!')
			else:
				# self.context.logoutputtogui('port already open!')
				pass
			
			self.storedcomsetup=arg

			if self.readerthread is not None:
				if not self.readerthread.isAlive():
					self.readerthread=ComReaderThread(self.comstream,self.threadq)
					self.readerthread.start()
			else:
				self.readerthread=ComReaderThread(self.comstream,self.threadq)
				self.readerthread.start()

			if self.reconnectorthread is not None:
				if not self.reconnectorthread.isAlive():
					self.reconnect(self.storedcomsetup,self.comstream)
			else:
				self.reconnect(self.storedcomsetup,self.comstream)
			
			return True
		except Exception as e:
			self.context.logoutputtogui('{}\n'.format(e))
			return False

	def reconnect(self,args,com):
		self.reconnectorthread=ReconnectorThread(args,com)
		self.reconnectorthread.start()

	def disconnect(self):
		self.readerthread.stop(0.01)
		self.reconnectorthread.stop(0.01)
		self.comstream.close()
			

	def sendCmd(self,cmd):
		self.comstream.write(cmd.encode())


	def getdata(self):
		return self.threadq.get(False)
	
	def sendScript(self, text):
		'''
		Takes a text with commands to send to the serial device
		Newline separated

		Syntax:
		
		command [*int] - sends command int (optional) times, e.g. c, c*10
		sleep [float] - sleeps for float ms, e.g. sleep 1000
		delay [float] - sets the delay time, float ms, between sending
		'''

		delay = 0.05 # default delay, if none or 0 given
		split_text = text.split('\n')

		for idx, line in enumerate(split_text):
			if not self.comstream.is_open:
				self.context.logoutputtogui('Port is not open\n')
				break

			if 'delay' in line:
				d = re.search('\d*\.\d+|\d+', line)

				try:
					parsedDelay = float(d.group(0))
					if parsedDelay == 0 or parsedDelay > 30000:
						delay = 0.05
					else:
						delay = parsedDelay / 1000

				except:
					self.context.logoutputtogui('Invalid format \'delay\' on row {}. Quitting.\n'
									.format(idx+1))
					break

			elif 'sleep' in line:
				s = re.search('\d*\.\d+|\d+', line)

				try:
					self.master.update()
					ss = float(s.group(0)) / 1000 
					time.sleep(ss)
					self.master.update()

				except:
					self.context.logoutputtogui('Invalid format \'sleep\' on row {}. Quitting.\n'
									.format(idx+1))
					break

			elif '*' in line:
				mult = line.split('*')

				for i in range(int(mult[1])):
					self.sendCmd(mult[0])
					self.master.update()
					time.sleep(delay)
					self.master.update()

			else:
				self.sendCmd(line)
				self.master.update()
				time.sleep(delay)
				self.master.update()

	
def getPorts():
	# lists all the available serial devices connected to the computer
	port_list = list_ports.comports()
	ports = [port.device for port in port_list]
	ports.append('Custom')
	return sorted(ports)


	