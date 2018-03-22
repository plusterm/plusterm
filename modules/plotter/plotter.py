import wx
from wx.lib.pubsub import pub
import re
import sys
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Plotter(wx.Frame):
    def __init__(self, parent, title):
        super(Plotter, self).__init__(parent, title=title, size=(640,480))
        pub.subscribe(self.plot_data, 'serial.data')

        self.figure = Figure(dpi=100)
        self.axes = self.figure.subplots(2, 1)

        self.canvasPanel = wx.Panel(self)
        self.canvas = FigureCanvas(self.canvasPanel, wx.ID_ANY, self.figure)
        self.canvasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvasSizer.Add(self.canvas, 1, flag=wx.ALL | wx.EXPAND)

        self.xdata = []
        self.ydata = []
        self.xdata2 = []
        self.ydata2 = []

        self.canvasPanel.SetSizer(self.canvasSizer)
        self.Show()

        self.Bind(wx.EVT_CLOSE, self.on_close)


    def on_close(self, event):
        del sys.modules['modules.plotter']
        del sys.modules['modules.plotter.plotter']
        pub.unsubscribe(self.plot_data, 'serial.data')
        event.Skip()


    def plot_data(self, data):
        numericData = re.findall("-?\d*\.\d+|-?\d+", data[1].decode(errors='ignore'))

        if len(numericData) == 1:
            self.axes[0].clear()
            self.xdata.append(float(data[0]))
            self.ydata.append(float(numericData[0]))
            self.axes[0].plot(self.xdata, self.ydata)

        elif len(numericData) == 2:
            self.axes[1].clear()
            self.xdata2.append(float(numericData[0]))
            self.ydata2.append(float(numericData[1]))
            self.axes[1].plot(self.xdata2, self.ydata2)

        self.canvas.draw()


p = Plotter(None, 'Plots')

def on_untick():
    p.Close()