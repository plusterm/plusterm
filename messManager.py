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
		"""	if the topic already exists in the dictionary append the subscriber
			to that topic. if not add topic (and subscriber) instead
		"""
		if topic in self.subscribers:
			self.subscribers[topic].append(subscriber)
		else:
			self.subscribers[topic]=[subscriber]

	def threadrunning(self):
		"""	returns the alive-staus of the thread delivering messages
		"""
		return self.messThread.isAlive()
		
	def send(self,message,topic):
		"""	checks if there are any subscribers and if there are, accepts the
			message and the topic putting it in the messagequeue as a tuple
			(topic, message)
		"""
		if len(self.subscribers) >0:
			self.messqueue.put((topic,message))

	def startdelivery(self):
		"""	if the message delivery thread is not "alive", start it
		"""
		if not self.messThread.isAlive():
			self.messThread.start()

	def stopdelivery(self):
		"""	if the message delivery thread is "alive", stop it
		"""
		if self.messThread.isAlive():
			self.messThread.stop()


class messengerThread(threading.Thread):
	"""	messengerThread handles the delivery of messages with it's running thread
	"""
	def __init__(self, subscribers,messqueue):
		threading.Thread.__init__(self)
		self.subscribers = subscribers	# dictionary containing interested moduleinstances by topic
		self.messque=messqueue	#	contains incomming data paired with topic
		self.alive=threading.Event()
		self.alive.set()
		
	def run(self):
		temp=tuple()
		while self.alive.isSet():
			try:	#	fetch the next item on the queue, a tuple (topic,message)
				temp=self.messque.get(False)
				#	for every topic found in subscribers
				for key in self.subscribers:
					#	check if the key matches the topic of the message
					if key==temp[0]:
						# for every subscriber interested in the topic
						for x in self.subscribers[key]:
							#deliver the message tuple
							x.receivedata(temp)
							
			except queue.Empty as e:
				#	if error occured becuase of an empty queue let some time
				#	pass before trying again
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


	