import wx
from wx.lib.pubsub import pub
import sys

class Multimeter(wx.Frame):
    def __init__(self, parent, title):
        super(Multimeter, self).__init__(parent, title=title)
        pub.subscribe(self.show_data, 'serial.data')

        self.multimeter_panel = wx.Panel(self)
        self.multimeter_output = wx.TextCtrl(self.multimeter_panel, style=wx.TE_READONLY, size=(250,50))
        self.multimeter_output.SetFont(wx.Font(wx.FontInfo(20)))

        self.multimeterSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.multimeterSizer.Add(self.multimeter_output)

        self.multimeter_panel.SetSizer(self.multimeterSizer)
        self.multimeterSizer.Fit(self)
        self.SetMinSize(self.GetSize())

        self.Show()
        self.Bind(wx.EVT_CLOSE, self.on_close)


    def show_data(self, data):
        data = data[1]
        self.multimeter_output.Clear()
        self.multimeter_output.AppendText(data)


    def on_close(self, event):
        del sys.modules['modules.multimeter']
        pub.unsubscribe(self.show_data, 'serial.data')
        event.Skip()

m = Multimeter(None, 'Multimeter')

def on_untick():
    m.Close()