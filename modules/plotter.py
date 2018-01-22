import os
from tkinter import *
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
from matplotlib import style
style.use('ggplot')

class plotter():
	"""	plotter fulfill all requirement of a plusterm-module.
		it may be ignoring the 'context' but it uses 'master' to extend the window,
		into which it desplays its results.
	"""
	def __init__(self,context,master):
		self.master = master
		# self.context=context
		self.setupPlot()


	def name(self):
		''' Checked when unticking the module in GUI '''
		return "plotter"


	def remove(self):
		''' Code to be run when unticking module in GUI '''
		self.destroyplot()
		

	def gettopics(self):
		"""	Return list of topics the module is interested in """
		topics = ["data"]
		return topics


	def receivedata(self, data):
		''' 
		Data sent from the serial monitor.
		Matches the serial output string with a regex. 
		If data read from serial is 1 numerical	value, plot it on the 
		y-axis with timestamp on the x-axis.
		If 2 numerical values are read, plot them (x,y) = (value1,value2).
		Data is a tuple of a tuple ("topic",(timestamp, data))
		'''
		
		if data[0] == "data":
			numericData = re.findall("-?\d*\.\d+|-?\d+", data[1][1].decode(errors='ignore'))
		
			if len(numericData) == 1:
				self.ax1.clear()		
				self.xValOne.append(data[1][0])
				self.yValOne.append(float(numericData[0]))

				if len(self.xValOne) > 90:
					self.xValOne.pop(0)
					self.yValOne.pop(0)

				#self.ax1.minorticks_on()
				self.ax1.plot(self.xValOne, self.yValOne, '.-')	
				# Rotate the x-ticks, to not overlap
				# self.ax1.tick_params(axis='x', rotation=30)			

			elif len(numericData) == 2:
				self.ax2.clear()
				self.xValTwo.append(float(numericData[0]))
				self.yValTwo.append(float(numericData[1]))

				if len(self.xValTwo) > 90:
					self.xValTwo.pop(0)
					self.yValTwo.pop(0)

				#self.ax2.minorticks_on()
				self.ax2.plot(self.xValTwo, self.yValTwo, '.-')
			
			#self.fig.tight_layout()	
			self.canvas.draw_idle()
		

	def setupPlot(self):
		# Sets up the plot, and frame containing the plot
		self.plotFrame = Frame(self.master)
		#self.plotFrame = Toplevel()

		clearPlotBtn = Button(self.plotFrame, text='Clear plot', command=self.clearPlot)
		clearPlotBtn.pack(pady=3)

		self.fig = Figure()
		self.ax1, self.ax2 = self.fig.subplots(2, 1)		

		self.canvas = FigureCanvasTkAgg(self.fig, self.plotFrame)
		self.canvas.get_tk_widget().pack(fill=BOTH, expand=True)

		toolbar = NavigationToolbar2TkAgg(self.canvas, self.plotFrame)
		toolbar.update()

		self.plotFrame.grid(column=1, row=0, rowspan=35)

		self.xValOne = []
		self.xValTwo = []
		self.yValOne = []
		self.yValTwo = []


	def destroyplot(self):
		# remove the plot
		self.plotFrame.destroy()
			

	def clearPlot(self):
		# Reset the plot figure
		self.ax1.clear()
		self.ax2.clear()
		self.xValOne = []
		self.xValTwo = []
		self.yValOne = []
		self.yValTwo = []
		self.canvas.draw_idle()
