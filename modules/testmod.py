
class testmod:
	"""docstring for testmod"""
	def __init__(self,context,master):
		pass
		
	def recivedata(self,data):
		"""	takes data as a tuple of topic and the actual data, which
			currently consist of 2 values (timestamp and the data read
			from the serialport) delivered from the readerthread.

		"""
		print("oh... i got some data: ")
		print(data)
		# print("\n")