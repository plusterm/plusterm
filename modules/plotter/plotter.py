import wx
from wx.lib.pubsub import pub
import re
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure

class Plotter(wx.Frame):
	def __init__(self):
		pub.subscribe(self.new_data, 'serial.data')

		self.plt = plt		
		self.fig, (self.ax1, self.ax2) = self.plt.subplots(2,1)

		self.xdata = []
		self.ydata = []
		self.xdata2 = []
		self.ydata2 = []

		self.plt.show()

	def new_data(self, data):
		numericData = re.findall("-?\d*\.\d+|-?\d+", data[1].decode(errors='ignore'))

		if len(numericData) == 1:
			self.ax1.clear()
			self.xdata.append(float(data[0]))
			self.ydata.append(float(numericData[0]))
			self.ax1.plot(self.xdata, self.ydata)

		elif len(numericData) == 2:
			self.ax2.clear()
			self.xdata2.append(float(numericData[0]))
			self.ydata2.append(float(numericData[1]))
			self.ax2.plot(self.xdata2, self.ydata2)

		self.plt.draw()

p = Plotter()