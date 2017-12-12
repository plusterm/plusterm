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

		# master.title("Serial Monitor")
		# master.protocol('WM_DELETE_WINDOW', self.onQuit)
		# master.resizable(0,0)
	
		# self.portVar = StringVar()
		# self.baudVar = StringVar()
		# self.plotVar = BooleanVar()
		# self.repeatVar = BooleanVar()

		# self.portVar.set('Custom')
		# self.baudVar.set('Custom')
		# self.repeatVar.set(False)
		# self.plotVar.set(False)

		# # self.plt = plt		
		# # self.ser = serial.Serial()

		# # self.threadq = queue.Queue()
		# # self.readThread = ComReaderThread(self.ser, self.threadq)

		# self.cmdList = list()

		# self.portChoices = self.getPorts()
		# self.baudratesList = [50, 75, 110, 134, 150, 200, 300, 600, 
		# 					1200, 1800, 2400, 4800, 9600, 19200, 38400, 
		# 					57600, 115200, 'Custom']


		# #### GUI elements
		
		# # Menu bar
		# menu = Menu(master)
		# master.config(menu=menu)

		# file = Menu(menu, tearoff=0)
		# file.add_command(label = 'Quit', underline=0, command=self.onQuit)
		# menu.add_cascade(label = 'File', underline=0, menu=file)

		# script = Menu(menu, tearoff=0)
		# script.add_command(label = 'Run', underline=0, command=self.openScriptFile)
		# menu.add_cascade(label = 'Script', underline=0, menu=script)

		# # Connection settings
		# settingsFrame = Frame(master)
		# self.portLabel = Label(settingsFrame, text='Device:')
		# self.popupMenuPort = OptionMenu(settingsFrame, self.portVar, *self.portChoices)
		# self.customPortEntry = Entry(settingsFrame, width=10)
		# self.baudLabel = Label(settingsFrame, text='     Baudrate:')
		# self.popupMenuBaud = OptionMenu(settingsFrame, self.baudVar, *self.baudratesList)
		# self.customBaudEntry = Entry(settingsFrame, width=10)
		# self.connectBtn = Button(settingsFrame, text='Open', command=self.connectSerial)
		# self.disconnectBtn = Button(settingsFrame, text='Close', command=self.disconnectSerial)

		# self.portLabel.pack(side='left')
		# self.popupMenuPort.pack(side='left')
		# self.customPortEntry.pack(side='left')
		# self.baudLabel.pack(side='left')
		# self.popupMenuBaud.pack(side='left')
		# self.customBaudEntry.pack(side='left')
		# self.connectBtn.pack(side='right', padx=17)
		# self.disconnectBtn.pack(side='right')
		# settingsFrame.grid(row=0, column=0, sticky=NSEW)

		# # Output
		# outputFrame = Frame(master)
		# self.scrollbar = Scrollbar(outputFrame)
		# self.textOutput = Text(outputFrame, height=30, width=80, takefocus=0, 
		# 	yscrollcommand=self.scrollbar.set, borderwidth=1, relief='sunken')
		# self.scrollbar.config(command=self.textOutput.yview)

		# self.textOutput.pack(side='left')
		# self.scrollbar.pack(side='right', fill=Y)
		# outputFrame.grid(row=1, column=0, sticky=NSEW)

		# # Input
		# inputFrame = Frame(master)
		# self.inputEntry = Entry(inputFrame, width=50)
		# self.inputEntry.bind('<Return>', self.onEnter)
		# self.inputEntry.bind('<Up>', self.onUpArrow)
		# self.inputEntry.bind('<Down>', self.onDownArrow)

		# self.sendBtn = Button(inputFrame, text='Send', command=self.onSendClick)
		# self.clearBtn = Button(inputFrame, text='Clear', command=self.clearOutput)

		# # Check if user wants a plot of the serial data
		# self.plotCheck = Checkbutton(inputFrame, text='Plot', onvalue=True, offvalue=False, 
		# 	variable=self.plotVar, command=self.setupPlot)

		# # Repeat commanda
		# self.repeatCheck = Checkbutton(inputFrame, text='Repeat:', onvalue=True, offvalue=False, 
		# 	variable=self.repeatVar, command=self.repeatMode)
		# self.repeatEntry = Entry(inputFrame, width=10)

		# self.inputEntry.pack(side='left')
		# self.sendBtn.pack(side='left')
		# self.clearBtn.pack(side='left')
		# self.repeatEntry.pack(side='right', padx=17, ipadx=0)
		# self.repeatCheck.pack(side='right')
		# self.plotCheck.pack(side='left')
		# inputFrame.grid(row=2, column=0, sticky=NSEW)


	# def getPorts(self):
	# 	# lists all the available devices connected to the computer
	# 	port_list = list_ports.comports()
	# 	ports = [port.device for port in port_list]

	# 	ports.append('Custom')
	# 	return sorted(ports)


	def connectSerial(self):
		self.communicator.connect()


	def disconnectSerial(self):
		try:
			self.master.after_cancel(self.listenComThread)
			self.readThread.stop(0.01)
			self.ser.close()
			self.textOutput.insert('end', 'Port closed\n')
		except Exception as e:
			self.textOutput.insert('end', '{}\n'.format(e))


	def listenComThread(self):
		try:
			result = self.threadq.get(False)
		except queue.Empty:
			pass
		else:
			self.logoutputtogui(result[1].decode())
			

			# If checkbutton for plot is set,add data to livefeed
			# to be used with plot function
			if self.plotVar.get() == True:
				self.plotter.Plot(result)

		# check again (unless program is quitting)
		try:
			self.master.after(10, self.listenComThread)	
		except:
			pass


	def onQuit(self):	
		# When closing the window, close serial connection and stop thread
		self.communicator.		

		self.master.quit()
		self.master.destroy()


	


	def onUpArrow(self, event):
		# cycles previously entered commands
		try:
			self.inputEntry.delete(0, 'end')
			self.cmdPointer -= 1

			if self.cmdPointer < 0:
				self.cmdPointer = 0

			self.inputEntry.insert('end', self.cmdList[self.cmdPointer])

		except:
			pass


	def onDownArrow(self, event):
		try:
			self.inputEntry.delete(0, 'end')
			self.cmdPointer += 1	
			self.inputEntry.insert('end', self.cmdList[self.cmdPointer])

		except:
			pass


	def onEnter(self, event):
		# sends command when enter is pressed
		cmd = self.inputEntry.get()
		self.sendCmd(cmd)


	def onSendClick(self):
		cmd = self.inputEntry.get()
		self.sendCmd(cmd)
					

	def repeatMode(self):
		# Repeat sends a command, by default evey 500 ms
		# Specify time limit with a comma, e.g. 'c, 100' in ms
		try:
			inp = self.repeatEntry.get().split(',')

			if len(inp) == 1:
				self.sendCmd(inp[0])
				timer = 500

			elif len(inp) == 2:
				self.sendCmd(inp[0])

				if int(inp[1]) <= 0:
					timer = 500
				else:
					timer = int(inp[1])

			# repeat
			if self.repeatVar.get() == True:
				try:
					self.master.after(timer, self.repeatMode)
				except:
					pass

		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))


	def sendCmd(self, cmd):
		try:
			self.ser.write(cmd.encode())

			localEcho = '> ' + cmd + '\n'
			self.logoutputtogui(localEcho)

		except Exception as e:
			self.logoutputtogui('{}\n'.format(e))	#.textOutput.insert('end', '{}\n'.format(e))

		finally:
			# Clear the entry widget, add save the last command
			self.inputEntry.delete(0, 'end')
			self.cmdList.append(cmd)

			# only save the 10 latest commands
			if len(self.cmdList) > 10:
				self.cmdList.pop(0)

			self.cmdPointer = len(self.cmdList)


	def setupPlot(self):
		# Sets up the plot, and frame containing the plot
		if self.plotVar.get() == True:
			self.plotFrame = Frame(self.master)
			clearPlotBtn = Button(self.plotFrame, text='Clear plot', command=self.clearPlot)
			clearPlotBtn.pack(pady=3)

			self.fig, (self.ax1, self.ax2) = self.plt.subplots(2,1)

			self.canvas = FigureCanvasTkAgg(self.fig, self.plotFrame)
			self.canvas.get_tk_widget().pack()

			toolbar = NavigationToolbar2TkAgg(self.canvas, self.plotFrame)
			toolbar.update()

			self.plotFrame.grid(column=1, row=0, rowspan=35)

			self.xValOne = []
			self.xValTwo = []
			self.yValOne = []
			self.yValTwo = []

			self.livePlot()

		else:
			# remove the plot
			self.plotFrame.destroy()


	def livePlot(self, data=None):
		''' 
		Matches the serial output string with a regex. 
		If data read from serial is 1 numerical	value, plot it on the 
		y-axis with timestamp on the x-axis.
		If 2 numerical values are read, plot them (x,y) = (value1,value2).
		Data from thread is a tuple (timestamp, data)
		'''

		if data is not None:
			numericData = re.findall("-?\d*\.\d+|-?\d+", data[1].decode())
		
			if len(numericData) == 1:
				self.ax1.clear()		
				self.xValOne.append(float(data[0]))
				self.yValOne.append(float(numericData[0]))

				if len(self.xValOne) > 50:
					self.xValOne.pop(0)
					self.yValOne.pop(0)

				self.ax1.minorticks_on()
				self.ax1.plot(self.xValOne, self.yValOne, '.-')

			elif len(numericData) == 2:
				self.ax2.clear()
				self.xValTwo.append(float(numericData[0]))
				self.yValTwo.append(float(numericData[1]))

				if len(self.xValTwo) > 50:
					self.xValTwo.pop(0)
					self.yValTwo.pop(0)

				self.ax2.minorticks_on()
				self.ax2.plot(self.xValTwo, self.yValTwo, '.-')

			self.canvas.draw()


	def clearPlot(self):
		# Reset the plot figure
		self.ax1.clear()
		self.ax2.clear()
		self.xValOne = []
		self.xValTwo = []
		self.yValOne = []
		self.yValTwo = []
		self.canvas.draw()


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

def main():
	root = Tk()
	app = SerialMonitor(root)
	root.mainloop()

if __name__ == '__main__':
	main()