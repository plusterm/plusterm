import wx
from wx.lib.pubsub import pub
import re
import sys
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas


class Plotter_adv(wx.Frame):
    def __init__(self, parent, title):
        super(Plotter_adv, self).__init__(parent, title=title)
        pub.subscribe(self.get_params, 'serial.data')

        self.plots_choices = ['1', '2', '3', '4', '5']
        self.nplot_sizerlist = []
        self.params = ['time']

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.init_ui()

    def init_ui(self):
        self.panel = wx.Panel(self)

        nplot_label = wx.StaticText(self.panel, label='How many plots? ')
        self.nplot_combo = wx.ComboBox(self.panel, choices=self.plots_choices)
        self.nplot_combo.Bind(wx.EVT_COMBOBOX, self.generate_plot_info)
        self.applybutton = wx.Button(self.panel, label='Apply')
        self.applybutton.Bind(wx.EVT_BUTTON, self.on_apply)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.nplot_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.nplot_sizer.Add(
            nplot_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.nplot_sizer.Add(
            self.nplot_combo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.nplot_sizer.Add(
            self.applybutton, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.mainSizer.Add(self.nplot_sizer)

        self.panel.SetSizerAndFit(self.mainSizer)
        self.Centre()
        self.Show(True)

    def get_params(self, data):
        a = re.findall(
            "(\w+)(: |, |,|:)(-?\d*\.\d+|-?\d+)",
            data[1].decode(errors='ignore'))

        for i in range(len(a)):
            if a[i][0] not in self.params:
                self.params.append(a[i][0])

    def generate_plot_info(self, event):
        n = self.nplot_combo.GetCurrentSelection() + 1

        if len(self.mainSizer.GetChildren()) - 1 > 0:
            self.clear_plot_info()

        for i in range(n):
            self.nplot_sizerlist.append(wx.BoxSizer(wx.HORIZONTAL))
            self.nplot_sizerlist[i].Add(
                wx.StaticText(self.panel, label='x: '))
            self.nplot_sizerlist[i].Add(
                wx.ComboBox(
                    self.panel,
                    style=wx.CB_READONLY,
                    choices=self.params))
            self.nplot_sizerlist[i].Add(
                wx.StaticText(
                    self.panel,
                    label='  y: '))
            self.nplot_sizerlist[i].Add(
                wx.ComboBox(
                    self.panel,
                    style=wx.CB_READONLY,
                    choices=self.params[1:]))
            self.mainSizer.Add(self.nplot_sizerlist[i])

        self.mainSizer.Layout()

    def clear_plot_info(self):
        nplotsizers = len(self.mainSizer.GetChildren()) - 1
        for i in range(nplotsizers, 0, -1):
            self.mainSizer.Hide(index=i)
            self.mainSizer.Remove(index=i)
            del self.nplot_sizerlist[i - 1]

    def on_apply(self, event):
        self.plot_window = Plotwindow(self, 'Plotwindow')
        # plot_window.Show()
        pub.unsubscribe(self.get_params, 'serial.data')

    def on_close(self, event):
        pub.unsubscribe(self.get_params, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.plotter_adv'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()


class Plotwindow(wx.Frame):
    def __init__(self, parent, title):
        super(Plotwindow, self).__init__(
            parent,
            title=title,
            size=(640, 480))
        pub.subscribe(self.plot_data, 'serial.data')

        self.nplots = len(settings.nplot_sizerlist)

        self.selected_params = []
        self.index_warned = False
        self.xdata = []
        self.ydata = []

        for i in range(self.nplots):
            self.xdata.append([])
            self.ydata.append([])
            children = settings.nplot_sizerlist[i].GetChildren()
            first = True
            for child in children:
                widget = child.GetWindow()
                if isinstance(widget, wx.ComboBox) and widget.GetValue():
                    if first:
                        p1 = widget.GetValue()
                        first = False
                    else:
                        self.selected_params.append([p1, widget.GetValue()])
                        first = True

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.init_ui()

    def init_ui(self):
        self.figure = Figure(dpi=100)

        self.axes = self.figure.subplots(self.nplots, 1)
        self.canvasPanel = wx.Panel(self)
        self.canvas = FigureCanvas(self.canvasPanel, wx.ID_ANY, self.figure)
        self.canvasSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.canvasSizer.Add(self.canvas, 1, flag=wx.ALL | wx.EXPAND)

        self.canvasPanel.SetSizer(self.canvasSizer)
        self.Show()

    def plot_data(self, data):
        a = re.findall(
            "(\w+)(: |, |,|:)(-?\d*\.\d+|-?\d+)",
            data[1].decode(errors='ignore'))

        for i in range(self.nplots):
            try:
                param_val_pair = [(d[0], d[2]) for d in a]
                px, py = self.selected_params[i]
                xfound = False
                yfound = False
                found_vals = {}

                for param, val in param_val_pair:
                    if not yfound and param == py:
                        found_vals['y'] = float(val)
                        yfound = True

                    if not xfound:
                        if param == px:
                            found_vals['x'] = float(val)
                            xfound = True

                        elif px == 'time':
                            found_vals['x'] = data[0]
                            xfound = True

                    if yfound and xfound:
                        self.xdata[i].append(found_vals['x'])
                        self.ydata[i].append(found_vals['y'])
                        break

                if self.nplots == 1:
                    self.axes.clear()
                    self.axes.plot(self.xdata[i], self.ydata[i], 'b.')

                else:
                    self.axes[i].clear()
                    self.axes[i].plot(self.xdata[i], self.ydata[i], 'b.')

            except IndexError:
                if not self.index_warned:
                    self.index_warned = True
                    dlg = wx.MessageDialog(
                        self,
                        message='Did you forget to set all parameters?',
                        caption='Index error')
                    dlg.SetOKLabel('Yes')
                    dlg.ShowModal()
                    del dlg

        self.canvas.draw()

    def on_close(self, event):
        pub.unsubscribe(self.plot_data, 'serial.data')
        event.Skip()


def dispose():
    settings.Close()


if __name__ == '__main__':
    app = wx.App()
    settings = Plotter_adv(None, 'Plotter settings')
    app.MainLoop()
else:
    settings = Plotter_adv(None, 'Plotter settings')
