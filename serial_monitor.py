from tkinter import *
from tkinter.filedialog import askopenfile

import serial
from serial.tools import list_ports

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
style.use('bmh')

import importlib

import queue
import re
import time

from com_reader import ComReaderThread
from types import SimpleNamespace

import communicator
import sm_gui
import plotter
import messManager

class SerialMonitor:
	'''
	Serial monitor GUI, plots, and controls
	'''
	def __init__(self, master):
		self.master = master
		self.messman=messManager.messManager()
		self.queue=queue.Queue()
		self.gui=sm_gui.sm_gui(master,self)
		self.plotter=plotter.plotter(master)
		self.communicator=communicator.communicator(self,self.queue)

	def connectSerial(self):
		"""	creates an arg structure with relevant info for a serialport connection
		"""
		arg=SimpleNamespace()	#	
		setattr(arg,"local",True)
		
		if self.gui.baudVar.get()=='Custom':
			setattr(arg,"baudrate",int(self.gui.customBaudEntry.get()))
		else:
			setattr(arg,"baudrate",int(self.gui.baudVar.get()))

		if self.gui.portVar.get()=='Custom':
			setattr(arg,"port",self.gui.customPortEntry.get())
		else:
			setattr(arg,"port",self.gui.portVar.get())
		
		setattr(arg,"timeout",0.01)

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

	# def setupPlot(self):
	# 	self.plotter.setupPlot()

	# def destroyplot(self):
	# 	self.plotter.destroyplot()
	
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
			self.logoutputtogui(result[1].decode())
			#	send data to messmanager
			self.messman.send(result,"data")
		
	def sendscript(text):
		"""	relays text to the communicator's sendscript function
		"""
		self.communicator.sendscript(text)

	def addmodule(self,modulename):
		"""	Dynamically imports a module located in the modules folder and
			instanciates it, adds it to the messManager subscriber dictionary,
			once for each topic the module is interested in.
			if the messManager deliverythread is not started (if it's the first
			module to be loaded), start it.
		"""
		#	import the module, more or less equivalent to:
		#	import 'modulename' as tmod
		mod=importlib.import_module("modules."+modulename)	#	load the code for the module
		tmod=getattr(mod,modulename)	#	create a python module of the code
		imod=tmod(self, self.master)	#	make an instance of the module

		#	for each topic returned from the gettopics function
		for topic in imod.gettopics():
			#	subscribe imod with the current topic
		 	self.messman.subscribe(imod,topic)
		 #	make sure that the messagedelivery is/gets started
		if not self.messman.threadrunning():
			self.messman.startdelivery()
		




def main():
	root = Tk()
	app = SerialMonitor(root)
	root.mainloop()

if __name__ == '__main__':
	main()