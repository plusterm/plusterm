import threading
from time import sleep

class ReconnectorThread(threading.Thread):
	"""docstring for reconnectorThread"""
	def __init__(self, arg,com):
		threading.Thread.__init__(self)
		self.arg = arg
		self.comstream=com

		self.alive=threading.Event()
		self.alive.set()

	def run(self):
		while self.alive.isSet():
			try:
				if self.arg.local:
					if not self.comstream.is_open:
						self.comstream.baudrate=self.arg.baudrate
						self.comstream.port=self.arg.port
						self.comstream.timeout=self.arg.timeout
						self.comstream.open()
					else:
						pass
				else:	#	remote eg server or p2p etc
					pass
			except Exception as e:
				print('reconnector:{}\n'.format(e))
			# else:
			# finally:
			# 	pass
			# 	pass
			sleep(0.5)

	def stop(self,timeout=None):
		self.alive.clear()
		threading.Thread.join(self,timeout)
