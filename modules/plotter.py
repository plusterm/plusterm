import os
from tkinter import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
style.use('bmh')

class plotter():
	"""plotter"""
	def __init__(self,context,master):
		# super(plotter, self).__init__()
		self.master = master
		# self.context=context
		self.plt = plt		
		self.plotFrame = Frame(self.master)
		self.setupPlot()
		
	def gettopics(self):
		topics=["data"]
		return topics	
	def setupPlot(self):
		# Sets up the plot, and frame containing the plot
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

		# self.livePlot()

	def destroyplot(self):
		# remove the plot
		self.plotFrame.destroy()

	def receivedata(self, data=None):
		''' 
		Matches the serial output string with a regex. 
		If data read from serial is 1 numerical	value, plot it on the 
		y-axis with timestamp on the x-axis.
		If 2 numerical values are read, plot them (x,y) = (value1,value2).
		Data is a tuple of a tuple ("topic",(timestamp, data))
		'''
		
		if data is not None and data[0]=="data":
			numericData = re.findall("-?\d*\.\d+|-?\d+", data[1][1].decode())
		
			if len(numericData) == 1:
				self.ax1.clear()		
				self.xValOne.append(float(data[1][0]))
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

