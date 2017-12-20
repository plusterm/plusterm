from pubsub import pub

class messManager:
	"""docstring for ClassName"""
	def __init__(self):
		self.subscribers={}


	def subscribe(self,subscriber,topic):
		if topic in subscribers:
			subscribers[topic].append(subscriber)
		else:
			subscribers[topic]=[subscriber]
		
		
	def send(self,message,topic):
		

	


class messengerThread(threading.Thread):
	"""docstring for messengerThread"""
	def __init__(self, que):
		threading.Thread.__init_(self)
		self.que = que
		


	def deliver():
		for key, subs in subscribers:
			if key==topic:
				for x in subs:
					x.recivedata(data)