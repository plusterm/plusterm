import wx
# from wx.lib.pubsub import pub
from pubsub import pub
import sys
import math
import pyttsx3
import re
import threading
import pythoncom

''' Requires the "pyttsx3" library for TTS. "python -m pip install pyttsx3".

    This module was build specifically for a Keysight Technologies U1232A
    Multimeter but should realistically work well with any multimeter in
    the Agilent U12xxx series. It displays either the most recent value or
    updates continuously depending on user choices. There is support for
    text-to-speech either via a button or automatically given a time interval.
    '''


class Multimeter(wx.Frame):
    def __init__(self, parent, title):
        super(Multimeter, self).__init__(parent, title=title)
        pub.subscribe(self.interpret_data, 'serial.data')

        self.prec_choices = ['1', '2', '3', '4', '5']
        self.prec = 3
        self.unit = ''
        self.ph_unit = ''
        self.unit_regex = '^\"(\w+)\,?|\"?'
        self.prefix_regex = '\d+E([\+\-]\d+)'
        self.looking_for_unit = False
        self.unit_found = False
        self.light_toggle = False

        self.init_ui()

    def init_ui(self):
        # Menu (acts only as a button of sorts)
        menubar = wx.MenuBar()
        tts_settings = wx.Menu()
        menubar.Append(tts_settings, '&TTS Settings')
        self.SetMenuBar(menubar)

        # Sizers and panels
        self.display_panel = wx.Panel(self)
        self.display_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.tts_panel = wx.Panel(self)
        self.tts_main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tts_sub_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.tts_sub_sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        self.controls_panel = wx.Panel(self)
        self.controls_main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.controls_sub_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_sub_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_sub_sizer3 = wx.BoxSizer(wx.HORIZONTAL)

        # Visible output panel widgets
        self.multimeter_output = wx.TextCtrl(
            self.display_panel,
            style=wx.TE_READONLY,
            size=(250, 50))
        self.multimeter_output.SetFont(wx.Font(wx.FontInfo(26)))

        self.display_sizer.Add(self.multimeter_output, 1, wx.EXPAND)

        # Multimeter control panel widgets
        fetch_button = wx.Button(
            self.controls_panel,
            label='Update data')
        fetch_button.Bind(wx.EVT_BUTTON, self.fetch_data)

        unit_button = wx.Button(
            self.controls_panel,
            label='Update unit')
        unit_button.Bind(wx.EVT_BUTTON, self.get_unit)

        light_button = wx.Button(
            self.controls_panel,
            label='Toggle display lighting')
        light_button.Bind(wx.EVT_BUTTON, self.toggle_light)

        beep_button = wx.Button(
            self.controls_panel,
            label='Beep')
        beep_button.Bind(wx.EVT_BUTTON, self.beep)

        self.value_spam = wx.CheckBox(
            self.controls_panel,
            label='Auto update data')

        prec_label = wx.StaticText(
            self.controls_panel,
            label='  Significant figures')

        self.prec_dd = wx.ComboBox(
            self.controls_panel,
            choices=self.prec_choices,
            style=wx.CB_READONLY)
        self.prec_dd.SetSelection(2)
        self.prec_dd.Bind(wx.EVT_COMBOBOX, self.set_precision)

        self.controls_sub_sizer1.Add(fetch_button, 0, wx.LEFT, 4)
        self.controls_sub_sizer1.Add(unit_button)
        self.controls_sub_sizer1.Add(
            self.value_spam,
            0,
            wx.LEFT | wx.ALIGN_CENTER_VERTICAL,
            5)
        self.controls_sub_sizer2.Add(light_button, 0, wx.LEFT, 4)
        self.controls_sub_sizer2.Add(beep_button)
        self.controls_sub_sizer3.Add(self.prec_dd, 0, wx.BOTTOM | wx.LEFT, 5)
        self.controls_sub_sizer3.Add(prec_label, 0, wx.ALIGN_CENTER_VERTICAL)

        self.controls_main_sizer.Add(self.controls_sub_sizer1)
        self.controls_main_sizer.Add(self.controls_sub_sizer2)
        self.controls_main_sizer.Add(self.controls_sub_sizer3)

        # Hidable tts panel widgets
        tts_line = wx.StaticLine(
            self.tts_panel,
            style=wx.LI_VERTICAL)

        talk_once_button = wx.Button(
            self.tts_panel,
            label='Talk once')
        talk_once_button.Bind(wx.EVT_BUTTON, self.talk)

        self.auto_talk_cb = wx.CheckBox(
            self.tts_panel,
            label=' Auto talk every')
        self.auto_talk_cb.Bind(wx.EVT_CHECKBOX, self.on_auto_talk)

        self.auto_talk_tc = wx.TextCtrl(
            self.tts_panel,
            size=(25, 20))
        self.auto_talk_tc.SetValue('5')

        auto_talk_st = wx.StaticText(self.tts_panel, label='seconds')

        self.tts_sub_sizer1.Add(talk_once_button, 0, wx.LEFT, 4)
        self.tts_sub_sizer2.Add(
            self.auto_talk_cb,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            5)
        self.tts_sub_sizer2.Add(
            self.auto_talk_tc,
            0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            3)
        self.tts_sub_sizer2.Add(
            auto_talk_st,
            0,
            wx.ALIGN_CENTER_VERTICAL | wx.LEFT,
            3)
        self.tts_main_sizer.Add(tts_line, 0, wx.EXPAND | wx.BOTTOM, 5)
        self.tts_main_sizer.Add(self.tts_sub_sizer1)
        self.tts_main_sizer.Add(self.tts_sub_sizer2)

        # Set sizers for panels
        self.tts_panel.SetSizer(self.tts_main_sizer)
        self.display_panel.SetSizer(self.display_sizer)
        self.controls_panel.SetSizer(self.controls_main_sizer)

        # Organize main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.display_panel, 0, wx.EXPAND | wx.BOTTOM, 5)
        self.main_sizer.Add(self.controls_panel, 0, wx.EXPAND)
        self.main_sizer.Add(self.tts_panel, 0, wx.EXPAND | wx.BOTTOM, 5)

        # Bindings
        self.Bind(wx.EVT_MENU_OPEN, self.on_menu)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Final gui settings
        self.SetBackgroundColour('lightgray')
        self.SetSizer(self.main_sizer)
        self.size_biggie = self.GetBestSize()
        self.tts_panel.Hide()
        self.Fit()
        self.size_smallz = self.GetBestSize()
        self.SetMinSize(self.size_smallz)
        self.SetMaxSize(self.size_smallz)
        self.Centre()
        self.Show(True)

    def fetch_data(self, event):
        pub.sendMessage('module.send', data='FETC?')

    def toggle_light(self, event):
        if not self.light_toggle:
            pub.sendMessage('module.send', data='SYST:BLIT 1')
            # self.multimeter_output.SetBackgroundColour("#FABB6E")
            # self.multimeter_output.Refresh()
            self.light_toggle = True
        else:
            pub.sendMessage('module.send', data='SYST:BLIT 0')
            # self.multimeter_output.SetBackgroundColour("lightgray")
            # self.multimeter_output.Refresh()
            self.light_toggle = False

    def beep(self, event):
        pub.sendMessage('module.send', data='SYST:BEEP TONE')

    def talk(self, event):
        try:
            if self.talk_string != '':
                threading.Thread(
                    target=talk_once, args=(self.talk_string,)).start()

        except AttributeError:
            threading.Thread(
                target=talk_once, args=('Don\'t be silly!',)).start()
            self.multimeter_output.Clear()
            self.multimeter_output.WriteText('No data.')

    def on_auto_talk(self, event):
        try:
            if self.auto_talk_cb.IsChecked():
                print('on auto talk')
                self.timer = wx.Timer()
                self.timer.Bind(wx.EVT_TIMER, self.on_timer)
                print(str(int(self.auto_talk_tc.GetValue())))
                self.timer.Start(int(self.auto_talk_tc.GetValue()) * 1000)
            else:
                self.timer.Stop()

        except Exception as e:
            print(e)

    def on_timer(self, event):
        print('on timer')
        self.talk(wx.EVT_BUTTON)

    def set_precision(self, event):
        self.prec = self.prec_dd.GetSelection() + 1

    def get_unit(self, event):
        self.looking_for_unit = True
        pub.sendMessage('module.send', data='CONF?')

    def interpret_data(self, data):
        '''This function is subscribed to the data stream.
        It interprets the data in order for the module to display it properly
        as well as to prepare a talk string for the tts functions. '''
        r = data[1].decode(errors='ignore').strip()
        if r.startswith('*'):
            return

        _prefixes_phonetic = {
            ' ': '',
            ' a': ' atto',
            ' f': ' femto',
            ' p': ' picko',
            ' n': ' nano',
            ' μ': ' micro',
            ' m': ' milli',
            ' k': ' kilo',
            ' M': ' mega',
            ' G': ' gihga',
            ' T': ' terra',
            ' P': ' peta',
            ' E': ' exa',
            ' Z': ' zetta'}

        _units_phonetic = [
            ['V', ' Volt', 'V'],
            ['DIOD', '', ''],
            ['RES', ' Ohm', 'Ω'],
            ['CAP', ' Fahrad', 'F'],
            ['A', ' Ampere', 'A'],
            ['FREQ', ' Hertz', 'Hz'],
            ['MV', ' Degrees Celsius', '°C']]

        val, prefix = None, None

        if self.looking_for_unit:
            unit_match = re.findall(self.unit_regex, r)
            for t in _units_phonetic:
                if unit_match[0] == t[0]:
                    self.unit = t[2]
                    self.ph_unit = t[1]
                    self.unit_found = True
                    self.looking_for_unit = False

        try:
            val = float(r)
            if not self.unit == '°C':
                val, prefix = self.to_si_2(val, self.prec)

        except ValueError:
            print('Not a float')
            pass

        self.talk_string = str(val)

        if self.unit_found and (val or val == 0):
            self.multimeter_output.Clear()
            if prefix:
                self.multimeter_output.WriteText(
                    self.talk_string + prefix + self.unit)
            else:
                self.multimeter_output.WriteText(
                    self.talk_string + self.unit)
        elif self.unit_found:
            print('Unit: ' + self.unit)
            pub.sendMessage('module.send', data='FETC?')

        if prefix and self.unit_found:
            self.talk_string += _prefixes_phonetic[prefix] + self.ph_unit
        elif self.unit_found and val and val != 'Inf ':
            self.talk_string += self.ph_unit

        if self.value_spam.IsChecked():
            pub.sendMessage('module.send', data='FETC?')

    def to_si_2(self, value, sig=3):
        # Thanks Simon!
        si_lookup = {
            7: ' Z',
            6: ' E',
            5: ' P',
            4: ' T',
            3: ' G',
            2: ' M',
            1: ' k',
            0: '',
            -1: ' m',
            -2: ' μ',
            -3: ' n',
            -4: ' p',
            -5: ' f',
            -6: ' a'
        }

        value = float(value)

        exp = math.floor(math.log10(abs(value)) / 3)

        if exp > 7:
            stuff = 'Inf '
            suffix = ''
        elif exp < -6:
            stuff = 'Zero '
        else:
            suffix = si_lookup[exp]

            stuff = '{0:1g}'.format(
                self.round_to_n(value / (10 ** (exp * 3)), sig))

        return stuff, suffix

    def round_to_n(self, x, n):
        x = round(x, -int(math.floor(math.log10(abs(x)))) + (n - 1))
        return x

    def on_close(self, event):
        pub.unsubscribe(self.interpret_data, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.multimeter'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()

    def on_menu(self, event):
        ''' size_biggie and size_smallz are size objects given before and after
        the tts menu panel was hidden. They act as size limits to prevent
        resizing of the multimeter frame. '''
        if not self.tts_panel.IsShown():
            self.SetMaxSize(self.size_biggie)
            self.SetMinSize(self.size_biggie)
            self.tts_panel.Show()

        else:
            self.tts_panel.Hide()
            self.SetMinSize(self.size_smallz)
            self.SetMaxSize(self.size_smallz)

        self.Layout()
        self.Fit()
        self.Update()


def dispose():
    m.Close()


def talk_once(talk_string):
    try:
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
        engine.say(talk_string)
        engine.runAndWait()
        engine.stop()
    except Exception as e:
        # It throws exceptions when called upon while still talking.
        # print(e)
        pass


if __name__ == '__main__':
    app = wx.App()
    m = Multimeter(None, 'Multimeter')
    app.MainLoop()
else:
    m = Multimeter(None, 'Multimeter')
