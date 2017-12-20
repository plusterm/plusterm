from tkinter import *
from tkinter.filedialog import askopenfile

import serial
from serial.tools import list_ports

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
style.use('bmh')

import queue
import re
import time

from com_reader import ComReaderThread
from types import SimpleNamespace

import communicator
import sm_gui
import plotter

class SerialMonitor:
	'''
	Serial monitor GUI, plots, and controls
	'''
	def __init__(self, master):
		self.master = master
		self.queue=queue.Queue()
		self.gui=sm_gui.sm_gui(master,self)
		self.plotter=plotter.plotter(master)
		self.communicator=communicator.communicator(self,self.queue)

	def connectSerial(self):
		arg=SimpleNamespace()
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
		try:
			self.communicator.disconnect()
			self.logoutputtogui('Port closed\n')
		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))

	def onQuit(self):	
		# When closing the window, close serial connection and stop thread
		self.disconnectSerial()

		self.master.quit()
		self.master.destroy()

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

	def setupPlot(self):
		self.plotter.setupPlot()
	def destroyplot(self):
		self.plotter.destroyplot()
	
	def logoutputtogui(self,data):
		self.gui.logoutput(data)

	def getdata(self):
		try:
			result = self.communicator.getdata()
		except queue.Empty:
			pass
		else:
			self.logoutputtogui(result[1].decode())
			

			# If checkbutton for plot is set,add data to livefeed
			# to be used with plot function
			if self.gui.plotVar.get() == True:
				self.plotter.Plot(result)
		
	def sendscript(text):
		self.communicator.sendscript(text)

def main():
	root = Tk()
	app = SerialMonitor(root)
	root.mainloop()

if __name__ == '__main__':
	main()