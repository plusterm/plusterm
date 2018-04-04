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
        data = data[1].decode(errors='ignore')
        self.multimeter_output.Clear()
        self.multimeter_output.WriteText(data)


    def on_close(self, event):
        pub.unsubscribe(self.show_data, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.multimeter'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()

m = Multimeter(None, 'Multimeter')

def dispose():
    m.Close()