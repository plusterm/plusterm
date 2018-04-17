import wx
from wx.lib.pubsub import pub
import sys
import pyttsx3
import re
import threading
import pythoncom

''' This module displays the current value given by a measuring instrument
    and has the support for text-to-speech either via a string trigger,
    a noise trigger or automatically given a time interval. '''


class Multimeter(wx.Frame):
    def __init__(self, parent, title):
        super(Multimeter, self).__init__(parent, title=title)
        pub.subscribe(self.interpret_data, 'serial.data')

        self.unit = ''
        self.ph_unit = ''
        self.looking_for_unit = False
        self.unit_regex = '^\"(\w+)\,?|\"?'
        self.prefix_regex = '\d+E([\+\-]\d+)'
        self.unit_found = False
        self.light_toggle = 0
        self.auto_talk = False
        self.talk_once = False

        self.init_ui()

    def init_ui(self):
        # Menu
        menubar = wx.MenuBar()
        tts_settings = wx.Menu()
        menubar.Append(tts_settings, '&TTS Settings')
        self.SetMenuBar(menubar)

        # Sizers and panels
        self.display_panel = wx.Panel(self)
        self.display_sizer = wx.BoxSizer(wx.VERTICAL)
        self.tts_panel = wx.Panel(self)
        self.tts_sizer = wx.BoxSizer(wx.VERTICAL)
        self.controls_panel = wx.Panel(self)
        self.controls_main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.controls_sub_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
        self.controls_sub_sizer2 = wx.BoxSizer(wx.HORIZONTAL)

        # These widgets will go in the always visible output panel
        self.multimeter_output = wx.TextCtrl(
            self.display_panel,
            style=wx.TE_READONLY,
            size=(250, 50))
        self.multimeter_output.SetFont(wx.Font(wx.FontInfo(24)))

        self.display_sizer.Add(self.multimeter_output)

        # These widgets will go in the multimeter control panel
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
            label='Continuous data')

        self.controls_sub_sizer1.Add(fetch_button)
        self.controls_sub_sizer1.Add(unit_button)
        self.controls_sub_sizer1.Add(self.value_spam)
        self.controls_sub_sizer2.Add(light_button)
        self.controls_sub_sizer2.Add(beep_button)

        self.controls_main_sizer.Add(self.controls_sub_sizer1)
        self.controls_main_sizer.Add(self.controls_sub_sizer2)

        # These widgets will go in the hidable tts panel
        talk_once_button = wx.Button(
            self.tts_panel,
            label='Talk once')
        talk_once_button.Bind(wx.EVT_BUTTON, self.talk_one_time)

        self.tts_sizer.Add(wx.StaticLine(self.tts_panel))
        self.tts_sizer.Add(talk_once_button)

        # Set sizers for panels
        self.tts_panel.SetSizer(self.tts_sizer)
        self.display_panel.SetSizer(self.display_sizer)
        self.tts_panel.SetSizer(self.tts_sizer)
        self.controls_panel.SetSizer(self.controls_main_sizer)

        # Organize main sizer
        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.display_panel)
        self.main_sizer.Add(self.controls_panel)
        self.main_sizer.Add(self.tts_panel)
        self.SetSizer(self.main_sizer)

        # Bindings
        self.Bind(wx.EVT_MENU_OPEN, self.on_menu)
        self.Bind(wx.EVT_CLOSE, self.on_close)

        # Final gui settings
        self.SetBackgroundColour('lightgray')
        self.tts_panel.Hide()
        self.Centre()
        self.Show(True)
        self.Fit()

    def fetch_data(self, event):
        pub.sendMessage('module.send', data='FETC?')

    def toggle_light(self, event):
        if not self.light_toggle:
            pub.sendMessage('module.send', data='SYST:BLIT 1')
            self.light_toggle = 1
        else:
            pub.sendMessage('module.send', data='SYST:BLIT 0')
            self.light_toggle = 0

    def beep(self, event):
        pub.sendMessage('module.send', data='SYST:BEEP TONE')

    def talk_one_time(self, event):
        try:
            if self.talk_string != '':
                threading.Thread(target=talk, args=(self.talk_string,)).start()
        except AttributeError:
            threading.Thread(target=talk, args=('Don\'t be silly!',)).start()
            self.multimeter_output.Clear()
            self.multimeter_output.WriteText('No data.')

    def get_unit(self, event):
        self.looking_for_unit = True
        pub.sendMessage('module.send', data='CONF?')

    def interpret_data(self, data):
        r = data[1].decode(errors='ignore').strip()

        self._prefixes_phonetic = {
            '': '',
            ' p': ' pico',
            ' n': ' nano',
            ' u': ' micro',
            ' m': ' milli',
            ' k': ' kilo',
            ' M': ' mega'
        }

        self._units_phonetic = [
            ['V', ' Volt', 'V'],
            ['DIOD', '', ''],
            ['RES', ' Ohm', 'Ω'],
            ['CAP', ' Fahrad', 'F'],
            ['A', ' Ampere', 'A'],
            ['FREQ', ' Hertz', 'Hz'],
            ['MV', ' Degrees Celsius', '°C']
        ]

        p = 2  # Precision, how many digits after point

        val = ''
        power = ''
        prefix = ''

        if self.looking_for_unit:
            unit_match = re.findall(self.unit_regex, r)
            for t in self._units_phonetic:
                if unit_match[0] == t[0]:
                    self.unit = t[2]
                    self.ph_unit = t[1]

                    self.unit_found = True
                    self.looking_for_unit = False

        try:
            val = float(r)
            if not self.unit == '°C':
                prefix_match = re.findall(self.prefix_regex, r)
                power = int(prefix_match[0])
                if power < -9:
                    val *= 10 ** 12
                    prefix = ' p'
                elif power < -6 and power >= -9:
                    val *= 10 ** 9
                    prefix = ' n'
                elif power < -3 and power >= -6:
                    val *= 10 ** 6
                    prefix = ' u'
                elif power < 0 and power >= -3:
                    val *= 10 ** 3
                    prefix = ' m'
                elif power >= 3 and power < 6:
                    val *= 10 ** -3
                    prefix = ' k'
                elif power >= 6 and power < 9:
                    val *= 10 ** -6
                    prefix = ' M'
                elif power >= 9:
                    val = 'inf '
                    power = ''
            try:
                val = round(val, p)
            except Exception:
                pass

        except ValueError:
            # print('Not a float')
            pass

        self.talk_string = str(val)

        if self.unit_found and val:
            self.multimeter_output.Clear()
            self.multimeter_output.WriteText(
                self.talk_string + prefix + self.unit)
        elif self.unit_found:
            self.multimeter_output.Clear()
            self.multimeter_output.WriteText('Unit: ' + self.unit)

        if prefix and self.unit_found:
            self.talk_string += self._prefixes_phonetic[prefix] + self.ph_unit
        elif self.unit_found and val and (val != 'inf'):
            self.talk_string += self.ph_unit

        if val and (self.auto_talk or self.talk_once):
            threading.Thread(target=talk, args=(self.talk_string,)).start()
            self.auto_talk, self.talk_once = False, False

        if self.value_spam.IsChecked():
            pub.sendMessage('module.send', data='FETC?')

    def on_close(self, event):
        pub.unsubscribe(self.interpret_data, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.multimeter'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()

    def on_menu(self, event):
        if not self.tts_panel.IsShown():
            self.tts_panel.Show()
            self.Layout()
            self.Fit()
            self.Update()
        else:
            self.tts_panel.Hide()
            self.Layout()
            self.Fit()
            self.Update()


def dispose():
    m.Close()


def talk(talk_string):
    try:
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
        # engine.setProperty('voice', 'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0')
        engine.say(talk_string)
        engine.runAndWait()
        # engine.stop()
    except Exception as e:
        # print(e)
        pass


if __name__ == '__main__':
    app = wx.App()
    m = Multimeter(None, 'Multimeter')
    app.MainLoop()
else:
    m = Multimeter(None, 'Multimeter')
