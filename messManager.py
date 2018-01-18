import threading
import queue
from time import sleep

class messManager:
	"""Class that manages the loaded modules as subscribers according to a pubsub system """
	def __init__(self):
		self.subscribers={}
		self.messqueue=queue.Queue()
		# global pause
		self.pause=True
		self.messThread=messengerThread(self.subscribers,self.messqueue,self)

	def subscribe(self,subscriber,topic):
		"""	if the topic already exists in the dictionary append the subscriber
			to that topic. if not add topic (and subscriber) instead
		"""
		self.pausedelivery()
		if topic in self.subscribers:
			self.subscribers[topic].append(subscriber)
		else:
			self.subscribers[topic]=[subscriber]
		self.resumedelivery()


	def threadrunning(self):
		"""	returns the alive-status of the thread delivering messages
		"""
		return self.messThread.isAlive()

		
	def send(self,message,topic):
		"""	checks if there are any subscribers and if there are, accepts the
			message and the topic putting it in the messagequeue as a tuple
			(topic, message)
		"""
		if len(self.subscribers) > 0:
			self.messqueue.put((topic,message))


	def startdelivery(self):
		"""	if the message delivery thread is not "alive", start it
		"""
		if not self.messThread.isAlive():
			self.messThread.start()
			# self.pause=False


	def stopdelivery(self):
		"""	if the message delivery thread is "alive", stop it
		"""
		if self.messThread.isAlive():
			self.messThread.stop()


	def removemodule(self,modulename):
		"""	checks every subscribers name and compares it to the given modulename

		"""
		self.pausedelivery()
		for key in self.subscribers:
			for subscriber in self.subscribers[key]:
				if subscriber.name() == modulename:
					subscriber.remove()	#	have the subscriber stop anything in it self that need stopping
					self.subscribers[key].remove(subscriber)	#	remove from list
		self.resumedelivery()


	def pausedelivery(self):
		self.pause=True
		sleep(0.2)


	def resumedelivery(self):
		self.pause=False

	
	def ispaused(self):
		return self.pause


class messengerThread(threading.Thread):
	"""	messengerThread handles the delivery of messages with it's running thread
	"""
	def __init__(self, subscribers,messqueue,pausevarholder):
		threading.Thread.__init__(self)
		self.manager=pausevarholder
		self.subscribers = subscribers	# dictionary containing interested moduleinstances by topic
		self.messque=messqueue	#	contains incomming data paired with topic
		self.alive=threading.Event()
		self.alive.set()
		

	def run(self):
		temp=tuple()
		while self.alive.isSet():

			while self.manager.ispaused():
				print("pausing for a bit...")
				sleep(0.1)

			try:	# fetch the next item on the queue, a tuple (topic,message)
				# print("atempting to get data")
				msg = self.messque.get(False)
				#print("success\ntrying to deliver data")
				#	for every topic found in subscribers
				
				for topic in self.subscribers:
					#for sub in self.subscribers[topic]:
					#	print(sub.name())

					#	check if the key matches the topic of the message
					if topic == msg[0]:
						# for every subscriber interested in the topic
						for sub in self.subscribers[topic]:
							#print("delivery attempt")
							#deliver the message tuple
							sub.receivedata(msg)
							#print("delivered")
				#print("delivery done")
							
			except queue.Empty as e:
				#	if error occured becuase of an empty queue let some time
				#	pass before trying again
				sleep(0.01)
				# print(e)

			except Exception as e:
				print("non queue related error:\n{}".format(e))
				print (e)


	def stop(self,timeout=None):
		self.alive.clear()
		threading.Thread.join(self,timeout)


