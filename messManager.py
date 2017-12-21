import threading
import queue

class messManager:
	"""docstring for ClassName"""
	def __init__(self):
		self.subscribers={}
		self.messqueue=queue.Queue()
		self.messThread=messengerThread(self.subscribers,self.messqueue)

	def subscribe(self,subscriber,topic):
		if topic in subscribers:
			subscribers[topic].append(subscriber)
		else:
			subscribers[topic]=[subscriber]
		
		
	def send(self,message,topic):
		self.messqueue.put((topic,message))

	def startdelivery():
		if not self.messThread.isSet():
			self.messThread.start()
	def stopdelivery():
		self.messThread.stop()


class messengerThread(threading.Thread):
	"""docstring for messengerThread"""
	def __init__(self, subscribers,messqueue):
		threading.Thread.__init__(self)
		self.subscribers = subscribers
		self.messque=messqueue
		self.alive=threading.Event()
		self.alive.set()
		
	def run(self):
		while self.alive.isSet():
			try:
				if not self.messqueue.empty():
					temp=self.messqueue.pop()
					for key, subs in subscribers:
						if key==temp[0]:
							for x in subs:
								x.recivedata(temp)
			except Exception as e:
				raise
			else:
				pass
			finally:
				pass

	def stop(self,timeout=None):
		self.alive.clear()
		threading.Thread.join(self,timeout)


	