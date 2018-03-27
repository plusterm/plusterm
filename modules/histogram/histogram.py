import wx
from wx.lib.pubsub import pub
import re
import sys
import matplotlib.pyplot as plt
from collections import Counter
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator

class Histogram(wx.Frame):
    def __init__(self, parent, title):
        super(Histogram, self).__init__(parent, title=title, size=(640,480))
        pub.subscribe(self.plot, 'serial.data')

        self.dataList = []
        self.dataDict = {}

        self.figure = Figure(dpi=100)
        self.canvasPanel = wx.Panel(self)
        self.canvas = FigureCanvas(self.canvasPanel, wx.ID_ANY, self.figure)

        self.canvasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvasSizer.Add(self.canvas, 1, flag=wx.ALL | wx.EXPAND)

        self.canvasPanel.SetSizer(self.canvasSizer)

        self.ax = self.figure.subplots(1, 1)
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.tick_params(axis='both', which='major', labelsize=6)
        #('ytick', labelsize=8)
        self.Show()

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        pub.unsubscribe(self.plot, 'serial.data')
        self.dataDict.clear()
        self.dataList.clear()

        # "unimport" from serial monitor
        mod_refs = [mod for mod in sys.modules 
        if mod.startswith('modules.histogram')]

        for mr in mod_refs:
            del sys.modules[mr]

        event.Skip()


    def plot(self, data):
        #show the n(=5) most common in desc order
        '''
        self.dataList.append(data[1].decode(errors='ignore').strip())
        self.dataDict.clear()
        self.dataDict = dict(Counter(self.dataList).most_common(5))
        '''
        #show for all data
        self.dataDict[data[1].decode(errors='ignore').strip()] = self.dataDict.get(data[1].decode(errors='ignore').strip(), 0) + 1
        self.ax.barh(list(self.dataDict.keys()), list(self.dataDict.values()), color='#CCD3F7', edgecolor='black')

        self.canvas.draw()

h = Histogram(None, 'Histogram')

def on_untick():
    h.Close()