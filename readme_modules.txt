this document is meant to clearify how to implement a new module
intended for the PlusTerm program.

1:	the new module must be a class and its constructor must take 2
	additional parameters. one of which	is the context aka the instance
	of serial_monitor (in its current naming state).
	the other parameter is the master, an instance of the tkinter (gui tool),
	which is inteded for when the new module needs to add to the gui.

2:	the new modules must have the functions gettopics(self): and
	recivedata(self,data):.
	"gettopics" must return a list of topics that the modules are interested
	in.
	"recivedata" must take the parameter 'data', what it actually does with
	the data is irrelevant.

3:	all module sourcefiles must be located in the subdirectory 'modules'.



Module Template:

class template:
	"""	
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

	def recivedata(self,data):
		"""	takes data as a tuple of topic and the actual data, which
			currently consist of 2 values (timestamp and the data read
			from the serialport) delivered from the readerthread.

		"""
		#do whatever you want with the data