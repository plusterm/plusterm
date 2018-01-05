
class testmod:
	"""	testmod: a very simple example module showing the structure and
		requirements of any module intended to subscribe on data in the
		serialmonitor application. a more complex, but also more complete
		example is the plotter-module found in plotter.py
	"""
	def __init__(self,context,master):
		"""	the constructor of all modules must take 2 variables: context
			and master (since it's python actual name can differ...).
			context is intended for if some functionallity need acces to
			for example, log something to the textarea in the gui, then it
			does so through the "context" which should be the instance
			of serial_monitor.
			master is intended for extending the gui and is suposed to be
			a tkinter.tk() instance
		"""
		self.context=context
		self.master=master
		
	def gettopics(self):
		"""	returns the topics that this module is interested in
		"""
		topics=["data"]
		return topics	
	def receivedata(self,data):
		"""	takes data as a tuple of topic and the actual data, which
			currently consist of 2 values (timestamp and the data read
			from the serialport) delivered from the readerthread.

		"""
		print("oh... i got some data: ")
		print(data)
		# print("\n")

