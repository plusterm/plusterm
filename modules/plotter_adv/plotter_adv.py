import wx
from wx.lib.pubsub import pub
import re
import sys
import time
from matplotlib.figure import Figure
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.backends.backend_wxagg import NavigationToolbar2WxAgg


class Plotter_adv(wx.Frame):
    def __init__(self, parent, title):
        super(Plotter_adv, self).__init__(parent, title=title)
        pub.subscribe(self.get_params, 'serial.data')

        self.plots_choices = ['1', '2', '3', '4', '5']
        self.nplot_sizerlist = []
        self.params = ['time']
        self.regex = "(\w+)(: |, |,|:)(-?\d*\.\d+|-?\d+)"
        self.cregex = re.compile(self.regex)
        self.group_role = []

        self.Bind(wx.EVT_CLOSE, self.on_close)

        self.init_ui()

    def init_ui(self):

        menubar = wx.MenuBar()
        advanced_settings = wx.Menu()
        menubar.Append(advanced_settings, '&Advanced Settings')
        self.Bind(wx.EVT_MENU_OPEN, self.toggle_adv_settings)
        self.SetMenuBar(menubar)

        self.regex_panel = wx.Panel(self)
        self.regex_sizer = wx.BoxSizer(wx.VERTICAL)

        preview_sizer = wx.BoxSizer(wx.HORIZONTAL)
        preview_label = wx.StaticText(self.regex_panel, label='Preview: ')
        self.preview_regex = wx.StaticText(self.regex_panel)

        preview_sizer.Add(preview_label)
        preview_sizer.Add(self.preview_regex)

        self.regex_sizer.Add(preview_sizer)

        self.regex_tb = wx.TextCtrl(
            self.regex_panel,
            style=wx.TE_PROCESS_ENTER,
            size=(400, 23))

        self.regex_group_sizer = wx.BoxSizer(wx.VERTICAL)
        self.choices = [
            'parameter name', 'value',
            'delimiter', 'value (without name)']

        # Initial regex settings
        group_label1 = wx.StaticText(self.regex_panel, label='Group 1')
        group_dd1 = wx.ComboBox(
            self.regex_panel, choices=self.choices, style=wx.CB_READONLY)
        group_dd1.Bind(wx.EVT_COMBOBOX, self.generate_group_role)
        group_dd1.SetSelection(0)
        self.regex_group_sizer.Add(group_label1)
        self.regex_group_sizer.Add(group_dd1)

        group_label2 = wx.StaticText(self.regex_panel, label='Group 2')
        group_dd2 = wx.ComboBox(
            self.regex_panel, choices=self.choices, style=wx.CB_READONLY)
        group_dd2.Bind(wx.EVT_COMBOBOX, self.generate_group_role)
        group_dd2.SetSelection(2)
        self.regex_group_sizer.Add(group_label2)
        self.regex_group_sizer.Add(group_dd2)

        group_label3 = wx.StaticText(self.regex_panel, label='Group 3')
        group_dd3 = wx.ComboBox(
            self.regex_panel, choices=self.choices, style=wx.CB_READONLY)
        group_dd3.Bind(wx.EVT_COMBOBOX, self.generate_group_role)
        group_dd3.SetSelection(1)
        self.regex_group_sizer.Add(group_label3)
        self.regex_group_sizer.Add(group_dd3)

        self.regex_tb.Bind(wx.EVT_TEXT_ENTER, self.on_enter_regex)
        self.regex_tb.SetValue(self.regex)
        self.generate_group_role(wx.EVT_TEXT_ENTER)

        self.regex_sizer.Add(self.regex_tb)
        self.regex_sizer.Add(self.regex_group_sizer)
        self.regex_panel.SetSizer(self.regex_sizer)

        self.panel = wx.Panel(self)

        nplot_label = wx.StaticText(self.panel, label='Number of plots: ')
        self.nplot_combo = wx.ComboBox(
            self.panel,
            choices=self.plots_choices,
            style=wx.CB_READONLY)
        self.nplot_combo.Bind(wx.EVT_COMBOBOX, self.generate_plot_info)

        self.plot_set_sizer = wx.BoxSizer(wx.VERTICAL)
        self.nplot_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.nplot_sizer.Add(
            nplot_label, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
        self.nplot_sizer.Add(
            self.nplot_combo, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)

        self.plot_set_sizer.Add(self.nplot_sizer)
        self.panel.SetSizer(self.plot_set_sizer)

        self.mainSizer = wx.BoxSizer(wx.VERTICAL)
        self.mainSizer.Add(self.regex_panel)
        self.mainSizer.Add(self.panel)

        self.SetBackgroundColour('lightgray')
        self.SetSizer(self.mainSizer)
        self.regex_panel.Hide()
        self.Centre()
        self.Show(True)

    def toggle_adv_settings(self, event):
        if not self.regex_panel.IsShown():
            self.regex_panel.Show()
            self.Layout()
            self.Fit()
            self.Update()
        else:
            self.regex_panel.Hide()
            self.Layout()
            # self.Fit()
            self.Update()

    def clear_regex_panel(self):
        nr = len(self.regex_group_sizer.GetChildren()) - 1
        if nr <= 0:
            return

        for i in range(nr, -1, -1):
            self.regex_group_sizer.Hide(index=i)
            self.regex_group_sizer.Remove(index=i)

    def on_enter_regex(self, event):
        self.clear_regex_panel()
        self.params = ['time']
        text = self.regex_tb.GetValue()

        try:
            self.cregex = re.compile(text)

        except Exception:
            dlg = wx.MessageDialog(
                self,
                message='The regular expression seems to be invalid',
                caption='Invalid regular expression')
            dlg.ShowModal()
            del dlg

        else:
            self.regex = text
            nr_groups = self.cregex.groups
            for i in range(nr_groups):
                label = 'Group {}'.format(i + 1)
                group_label = wx.StaticText(self.regex_panel, label=label)
                group_dd = wx.ComboBox(
                    self.regex_panel,
                    choices=self.choices,
                    style=wx.CB_READONLY)
                group_dd.Bind(wx.EVT_COMBOBOX, self.generate_group_role)
                self.regex_group_sizer.Add(group_label)
                self.regex_group_sizer.Add(group_dd)

            self.regex_panel.Update()
            self.Layout()
            self.Fit()

    def get_params(self, data):
        a = self.cregex.findall(data[1].decode(errors='ignore').strip())
        if self.regex_panel.IsShown():
            self.preview_regex.SetLabel(
                str(a).replace('[', '').replace(']', ''))

        for match in a:
            for g_ind, r in self.group_role:
                if r == 'value (without name)':
                    if 'val' + str(g_ind) not in self.params:
                        self.params.append('val' + str(g_ind))

                if r == 'parameter name':
                    if match[g_ind] not in self.params:
                        self.params.append(match[g_ind])

    def generate_plot_info(self, event):
        n = self.nplot_combo.GetCurrentSelection() + 1

        if len(self.plot_set_sizer.GetChildren()) - 1 > 0:
            self.clear_plot_info()

        for i in range(n):
            self.nplot_sizerlist.append(wx.BoxSizer(wx.HORIZONTAL))
            self.nplot_sizerlist[i].Add(
                wx.StaticText(self.panel, label=' x: '))
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
            self.plot_set_sizer.Add(self.nplot_sizerlist[i])

        self.applybutton = wx.Button(self.panel, label='Plot')
        self.applybutton.Bind(wx.EVT_BUTTON, self.on_apply)
        self.plot_set_sizer.Add(
            self.applybutton,
            0,  # Not stretchable
            wx.ALIGN_LEFT | wx.ALL,  # Left aligned, border on all sides
            5)  # Border size

        self.panel.Update()
        self.Layout()
        self.SetSizer(self.mainSizer)

    def generate_group_role(self, event):
        self.params = ['time']
        self.group_role = []
        for ind, child in enumerate(self.regex_group_sizer.GetChildren()):
            widget = child.GetWindow()

            if isinstance(widget, wx.StaticText):
                i = int(widget.GetLabel()[-1]) - 1
                continue

            if isinstance(widget, wx.ComboBox):
                t = widget.GetValue()
                self.group_role.append((i, t))

    def clear_plot_info(self):
        # This was changed with the new apply button
        nplotsizers = len(self.nplot_sizerlist)
        for i in range(nplotsizers + 1, 0, -1):
            self.plot_set_sizer.Hide(index=i)
            self.plot_set_sizer.Remove(index=i)
            # del nplot_sizerlist[i]
        self.nplot_sizerlist = []

    def on_apply(self, event):
        self.generate_group_role(wx.EVT_COMBOBOX)
        self.plot_window = Plotwindow(self, 'Plotwindow')
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

        menubar = wx.MenuBar()
        export = wx.Menu()

        menubar.Append(export, 'Export to CSV')
        self.SetMenuBar(menubar)
        self.Bind(wx.EVT_MENU_OPEN, self.save_csv)

        self.figure = Figure(dpi=75)

        if self.nplots == 1:
            self.axes = []
            self.axes.append(self.figure.subplots(self.nplots, 1))

        else:
            self.axes = self.figure.subplots(self.nplots, 1)

        self.canvasPanel = wx.Panel(self)
        self.canvas = FigureCanvas(self.canvasPanel, wx.ID_ANY, self.figure)
        self.canvasSizer = wx.BoxSizer(wx.VERTICAL)
        self.canvasSizer.Add(self.canvas, 1, flag=wx.ALL | wx.EXPAND)

        self.canvas_toolbar = NavigationToolbar2WxAgg(self.canvas)
        self.canvas_toolbar.Realize()
        self.canvasSizer.Add(self.canvas_toolbar, 0, wx.ALL | wx.EXPAND)
        self.canvas_toolbar.Update()
        self.canvasPanel.SetSizer(self.canvasSizer)
        # set t0
        self.t0 = time.time()
        self.Show()

    def plot_data(self, data):
        a = settings.cregex.findall(data[1].decode(errors='ignore').strip())
        for i in range(self.nplots):
            try:
                param_val_pair = []
                group_role = settings.group_role
                for match in a:
                    param, val = None, None
                    for g_ind, r in group_role:
                        if r == 'value (without name)':
                            param = 'val' + str(g_ind)
                            val = match[g_ind]

                        elif r == 'parameter name':
                            param = match[g_ind]

                        elif r == 'value':
                            val = match[g_ind]

                        if param and val:
                            param_val_pair.append((param, val))

                px, py = self.selected_params[i]
                xfound = False
                yfound = False
                found_vals = {}
                for (param, val) in param_val_pair:
                    if not yfound and param == py and val != '':
                        found_vals['y'] = float(val)
                        yfound = True

                    if not xfound:
                        if param == px and val != '':
                            found_vals['x'] = float(val)
                            xfound = True

                        elif px == 'time':
                            found_vals['x'] = data[0] - self.t0
                            xfound = True

                    if yfound and xfound:
                        self.xdata[i].append(found_vals['x'])
                        self.ydata[i].append(found_vals['y'])

                self.axes[i].clear()
                self.axes[i].plot(self.xdata[i], self.ydata[i], '.-')
                self.axes[i].set_xlabel(px)
                self.axes[i].set_ylabel(py)

            except IndexError as e:
                if not self.index_warned:
                    self.index_warned = True
                    dlg = wx.MessageDialog(
                        self,
                        message='Did you forget to set all parameters?\n',
                        caption='Index error')
                    dlg.SetOKLabel('Sorry')
                    dlg.ShowModal()
                    del dlg

        try:
            self.canvas.draw()

        except Exception:
            pass

    def save_csv(self, event):
        fd = wx.FileDialog(
            self,
            "Save file",
            wildcard='Text files (*.txt)|*.txt',
            style=wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT)

        if fd.ShowModal() == wx.ID_CANCEL:
            return

        else:
            pathname = fd.GetPath()
            with open(pathname, 'w') as file:
                # write header
                header = 'plot_nr, x, y\n'
                file.write(header)
                for i, ax in enumerate(self.axes):
                    line = ax.lines[0]
                    x_data = line.get_xdata()
                    y_data = line.get_ydata()
                    for x, y in zip(x_data, y_data):
                        data = '{}, {}, {}\n'.format(i + 1, x, y)
                        file.write(data)

    def on_close(self, event):
        pub.unsubscribe(self.plot_data, 'serial.data')
        pub.subscribe(settings.get_params, 'serial.data')
        event.Skip()


def dispose():
    settings.Close()


if __name__ == '__main__':
    app = wx.App()
    settings = Plotter_adv(None, 'Plotter settings')
    app.MainLoop()
else:
    settings = Plotter_adv(None, 'Plotter settings')
