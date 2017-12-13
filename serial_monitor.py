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

import communicator
import sm_gui
import plotter

class SerialMonitor:
	'''
	Serial monitor GUI, plots, and controls
	'''
	def __init__(self, master):
		self.master = master
		self.gui=sm_gui.sm_gui(master,self)
		self.plotter=plotter.plotter(master)
		self.communicator=communicator.communicator()

	def connectSerial(self):
		self.communicator.connect()


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
			self.communicator.sendCmd(cmd.encode())

			localEcho = '> ' + cmd + '\n'
			self.logoutputtogui(localEcho)

		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))	

		finally:
			# Clear the entry widget, add save the last command
			self.gui.clearinputentry()
			self.gui.savecommand(cmd)

	def openScriptFile(self):
		file = askopenfile(filetypes =(("Text File", "*.txt"),("All Files","*.*")),
							title = "Choose a file")
		try:
			f = open(file.name, 'r')
			text = f.read()
			f.close()
			self.sendScript(text)
				
		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))


	def sendScript(self, text):
		'''
		Takes a text with commands to send to the serial device
		Newline separated

		Syntax:
		
		command [*int] - sends command int (optional) times, e.g. c, c*10
		sleep [float] - sleeps for float ms, e.g. sleep 1000
		delay [float] - sets the delay time, float ms, between sending
		'''

		delay = 0.05 # default delay, if none or 0 given
		split_text = text.split('\n')

		for idx, line in enumerate(split_text):
			if not self.ser.is_open:
				self.logoutputtogui('Port is not open\n')
				break

			if 'delay' in line:
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
				self.sendCmd(line)
				self.master.update()
				time.sleep(delay)
				self.master.update()

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
			if self.plotVar.get() == True:
				self.plotter.Plot(result)
		

def main():
	root = Tk()
	app = SerialMonitor(root)
	root.mainloop()

if __name__ == '__main__':
	main()