import wx
from wx.lib.pubsub import pub
import re
import sys
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas

class Histogram(wx.Frame):
    def __init__(self, parent, title):
        super(Histogram, self).__init__(parent, title=title, size=(640,480))
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
        pub.unsubscribe(self.plot_data, 'serial.data')

        # "unimport" from serial monitor
        mod_refs = [mod for mod in sys.modules 
        if mod.startswith('modules.histogram')]

        for mr in mod_refs:
            del sys.modules[mr]

        event.Skip()


    def plot_data(self, data):


p = Histogram(None, 'Histogram')

def on_untick():
    p.Close()