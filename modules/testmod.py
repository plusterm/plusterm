
class testmod:
	"""	testmod: a very simple example module showing the structure and
		requirements of any module intended to subscribe on data in the
		serialmonitor application
	"""
	def __init__(self,context,master):
		"""	the constructor of all modules must take 2 variables: context
			and master (since it's python actual name can differ...).
			context is intended for if some functionallity need acces to
			for example, log something to the textarea in the gui.
			master is intended for extending the gui and is suposed to be
			a tkinter.tk() instance
		"""
		pass
	def gettopics(self):
		"""	returns the topics that this module is interested in
		"""
		topics=["data"]
		return topics	
	def recivedata(self,data):
		"""	takes data as a tuple of topic and the actual data, which
			currently consist of 2 values (timestamp and the data read
			from the serialport) delivered from the readerthread.

		"""
		print("oh... i got some data: ")
		print(data)
		# print("\n")