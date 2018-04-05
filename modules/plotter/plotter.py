import wx
from wx.lib.pubsub import pub
import re
import sys
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Plotter(wx.Frame):
    def __init__(self, parent, title):
        super(Plotter, self).__init__(parent, title=title, size=(640,480))
        pub.subscribe(self.plot_data, 'serial.data')

        self.figure = Figure(dpi=100)
        #self.axes = self.figure.subplots(2, 1)

        self.ax1 = self.figure.add_subplot(2, 1, 1)
        self.ax2 = self.figure.add_subplot(2, 1, 2, projection = '3d')

        self.canvasPanel = wx.Panel(self)
        self.canvas = FigureCanvas(self.canvasPanel, wx.ID_ANY, self.figure)
        self.canvasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvasSizer.Add(self.canvas, 1, flag=wx.ALL | wx.EXPAND)

        self.xdata = []
        self.ydata = []
        self.xdata2 = []
        self.ydata2 = []
        self.zdata =  []

        self.canvasPanel.SetSizer(self.canvasSizer)
        self.Show()

        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_close(self, event):
        pub.unsubscribe(self.plot_data, 'serial.data')

        # "unimport" from serial monitor
        mod_refs = list(
            filter(lambda m: m.startswith('modules.plotter'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]

        event.Skip()


    def plot_data(self, data):
        numericData = re.findall("-?\d*\.\d+|-?\d+", 
            data[1].decode(errors='ignore'))

        if len(numericData) == 1:
            self.ax1.clear()
            self.xdata.append(float(data[0]))
            self.ydata.append(float(numericData[0]))
            self.ax1.plot(self.xdata, self.ydata)

        elif len(numericData) == 2:
            self.ax2.clear()
            self.xdata2.append(float(numericData[0]))
            self.ydata2.append(float(numericData[1]))
            self.zdata.append(float(data[0]))
            self.ax2.scatter(self.ydata2, self.xdata2, self.zdata)

        self.canvas.draw()


p = Plotter(None, 'Plots')

def dispose():
    p.Close()