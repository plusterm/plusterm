from tkinter import *
from tkinter.filedialog import askopenfile

import serial
from serial.tools import list_ports

import importlib

import queue
import re
import time

from com_reader import ComReaderThread
from types import SimpleNamespace

import communicator
import sm_gui
import messManager

class SerialMonitor:
	'''
	Central class ("context") for the Serial Monitor and modules
	'''
	def __init__(self, master):
		self.master = master
		self.messman=messManager.messManager()
		self.gui=sm_gui.sm_gui(master,self)
		self.communicator=communicator.communicator(self)

	def connectSerial(self):
		"""	creates an arg structure with relevant info for a serialport connection
			and try to connect with that arg structure
		"""
		arg=SimpleNamespace()	#	
		setattr(arg,"local",True)

		#	get the baudrate from the textbox or the the chosen
		if self.gui.baudVar.get() == 'Custom':
			setattr(arg,"baudrate",int(self.gui.customBaudEntry.get()))

		else:
			setattr(arg,"baudrate",int(self.gui.baudVar.get()))

		#	get the port from the textbox or the the chosen
		if self.gui.portVar.get() == 'Custom':
			setattr(arg,"port",self.gui.customPortEntry.get())

		else:
			setattr(arg,"port",self.gui.portVar.get())

		#	set timeout 
		setattr(arg,"timeout",0.01)
		#	attempt connection

		if self.communicator.connect(arg):
			self.logoutputtogui("communication open\n")

		else:
			pass


	def disconnectSerial(self):
		"""	attempt to disconnect communications and log the result/error to the gui
		"""
		try:
			self.communicator.disconnect()
			self.logoutputtogui('Port closed\n')

		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))


	def onQuit(self):	
		# When closing the window, close serial connection and stop threads
		self.disconnectSerial()
		self.messman.stopdelivery()
		self.master.quit()
		self.master.destroy()
		# for x in self.messman.:
		# 	pass


	def sendCmd(self, cmd):
		try:
			self.communicator.sendCmd(cmd)

			localEcho = '> ' + cmd + '\n'
			self.logoutputtogui(localEcho)

		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))	

		finally:
			# Clear the entry widget, add save the last command
			self.gui.clearinputentry()
			self.gui.savecommand(cmd)

		
	def logoutputtogui(self,data):
		"""	relays data to be "printed" to the gui's logoutput function
		"""
		self.gui.logoutput(data)


	def getdata(self):
		"""	gets data from the readerthread and sends the data with the topic "data"
			to the messManager 
		"""
		try:
			result = self.communicator.getdata()

		except queue.Empty:	#	if fetching the data fails due to an empty queue
			pass			#	do nothing

		else:
			#	"print" data to gui (without the timestamp)
			self.logoutputtogui(result[1].decode(errors='replace'))
			#	send data to messmanager
			self.messman.send(result,"data")


	def sendScript(self, text):
			'''
			Takes a text with commands to send to the serial device
			Newline separated
	
			Syntax:
			command [*int] - sends command int (optional) times, e.g. 'c', 'c*10'
			sleep [int] - sleeps for int ms, e.g. 'sleep 1000'
			delay [int] - sets the delay time, int ms, between sending, e.g. 'delay 500'
			'''
	
			delay = 0.05 # default delay, if none or 0 given
			split_text = text.split('\n')
	
			for idx, line in enumerate(split_text):
				if self.communicator.comstream is None or not self.communicator.comstream.is_open:
					self.logoutputtogui('Port is not open\n')
					break
	
				if 'delay' in line:
					# ignore minus signs
					d = re.search('\d*\.\d+|\d+', line)
	
					try:
						parsedDelay = float(d.group(0))
						if parsedDelay == 0 or parsedDelay > 30000:
							delay = 0.05
						else:
							delay = parsedDelay / 1000
	
					except:
						self.logoutputtogui('Invalid format \'delay\' on row {}. Quitting.\n'
										.format(idx+1))
						break
	
				elif 'sleep' in line:
					s = re.search('\d*\.\d+|\d+', line)
	
					try:
						self.master.update()
						ss = float(s.group(0)) / 1000 
						time.sleep(ss)
						self.master.update()
	
					except:
						self.logoutputtogui('Invalid format \'sleep\' on row {}. Quitting.\n'
										.format(idx+1))
						break
	
				elif '*' in line:
					mult = line.split('*')
	
					for i in range(int(mult[1])):
						self.sendCmd(mult[0])
						self.master.update()
						time.sleep(delay)
						self.master.update()
	
				else:
					self.communicator.sendCmd(line)
					self.master.update()
					time.sleep(delay)
					self.master.update()
	

	def addmodule(self,modulename):
		"""	Dynamically imports a module located in the modules folder and
			instantiates it, adds it to the messManager subscriber dictionary,
			once for each topic the module is interested in.
			if the messManager deliverythread is not started (if it's the first
			module to be loaded), start it.
		"""
		#	importing of the module, more or less equivalent to:
		#	import 'modulename' as tmod
		mod = importlib.import_module("modules."+modulename)	#	load the code for the module
		tmod = getattr(mod,modulename)	#	create a python module of the code
		imod = tmod(self, self.master)	#	make an instance of the module

		#	for each topic returned from the gettopics function
		# self.messman.pausedelivery()
		for topic in imod.gettopics():
			#	subscribe imod with the current topic
		 	self.messman.subscribe(imod,topic)

		# self.messman.resumedelivery()
		#	make sure that the messagedelivery is/gets started
		if not self.messman.threadrunning():
			self.messman.startdelivery()

		
	def removemodule(self, modulename):
		self.messman.removemodule(modulename)		


def main():
	root = Tk()
	app = SerialMonitor(root)
	root.mainloop()

if __name__ == '__main__':
	main()
