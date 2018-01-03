import threading
import queue
from time import sleep

class messManager:
	"""docstring for ClassName"""
	def __init__(self):
		self.subscribers={}
		self.messqueue=queue.Queue()
		self.messThread=messengerThread(self.subscribers,self.messqueue)

	def subscribe(self,subscriber,topic):
		if topic in self.subscribers:
			self.subscribers[topic].append(subscriber)
		else:
			self.subscribers[topic]=[subscriber]
	def threadrunning(self):
		return self.messThread.isAlive()
		
	def send(self,message,topic):
		if len(self.subscribers) >0:
			self.messqueue.put((topic,message))

	def startdelivery(self):
		if not self.messThread.isAlive():
			self.messThread.start()

	def stopdelivery(self):
		if self.messThread.isAlive():
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
		temp=tuple()
		while self.alive.isSet():
			try:
				temp=self.messque.get(False)
				
				for key in self.subscribers:
					
					if key==temp[0]:
						for x in self.subscribers[key]:
							x.receivedata(temp)
							
			except queue.Empty as e:
				sleep(0.01)
				# print(e)
			except Exception as e:
				print("non queue related error:\n"+e)
			else:
				pass
				# print(temp[0]+": "+str(temp[1][0])+", "+str(temp[1][1]))	#	.__repr__()
			# finally:
			# 	pass

	def stop(self,timeout=None):
		self.alive.clear()
		threading.Thread.join(self,timeout)


	