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
        pub.subscribe(self.gather_data, 'serial.data')

        self.init_ui()

    def init_ui(self):
        menubar = wx.MenuBar()
        advanced_settings = wx.Menu()
        menubar.Append(advanced_settings, '&TTS Settings')
        self.Bind(wx.EVT_MENU_OPEN, self.toggle_adv_settings)
        self.SetMenuBar(menubar)

        self.multimeter_panel = wx.Panel(self)
        self.tts_panel = wx.Panel(self)

        self.multimeter_output = wx.TextCtrl(
            self.multimeter_panel,
            style=wx.TE_READONLY,
            size=(250, 50))
        self.multimeter_output.SetFont(wx.Font(wx.FontInfo(20)))

        tts_test1 = wx.StaticText(self.tts_panel, label='test1')
        tts_test2 = wx.StaticText(self.tts_panel, label='test2')
        tts_test3 = wx.StaticText(self.tts_panel, label='test3')
        tts_test4 = wx.StaticText(self.tts_panel, label='test4')

        self.tts_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tts_test_sizer = wx.BoxSizer(wx.VERTICAL)
        
        self.tts_sizer.Add(tts_test1)
        self.tts_sizer.Add(tts_test2)
        self.tts_sizer.Add(tts_test3)
        self.tts_sizer.Add(tts_test4)
        self.tts_sizer.Add(self.tts_panel)

        self.output_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.output_sizer.Add(self.multimeter_panel)

        self.main_sizer = wx.BoxSizer(wx.VERTICAL)
        self.main_sizer.Add(self.output_sizer)
        self.main_sizer.Add(self.tts_sizer)

        self.SetSizer(self.main_sizer)
        self.SetBackgroundColour('lightgray')
        self.tts_panel.Hide()
        self.Show(True)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def gather_data(self, data):
        data = data[1].decode(errors='ignore')
        self.multimeter_output.Clear()
        self.multimeter_output.WriteText(data)
        ''' to talk
        t = threading.Thread(target=self.talk)
        t.start()
        '''

    def interpret_string(self, string):
        _prefixes_phonetic = {
            'y': ' yocto',
            'z': ' zepto',
            'a': ' atto',
            'f': ' femto',
            'p': ' pico',
            'n': ' nano',
            'u': ' micro',
            'm': ' milli',
            'c': ' centi',
            'd': ' deci',
            'k': ' killo',
            'M': ' mega',
            'G': ' gihga',
            'T': ' terra',
            'P': ' peta',
            'E': ' exa',
            'Z': ' zetta',
            'Y': ' yotta'
        }

        _units_phonetic = {
            'K': ' Kelvin',
            'V': ' Volt',
            'A': ' Ampere',
            'J': ' Joole',
            'Hz': ' Hertz',
            'm': ' Meter',
            'bz': ' Bizzles',
            'ohm': ' Ohm',
            'W': ' Watt',
            '°C': ' Degrees Celsius',
            'C': ' Centigrade'
        }

        # Search string, to be replaced with subscribed data
        n = 'Voltage: 1234V'

        # Finds last digit. n[m.start()] gives it's index
        m = re.search('(\d)[^\d]*$', n)
        # Finds value, last group with a number of digits.
        val = re.findall('(-?\d+)', n)

        p = 0  # How many digits after the point
        i = 1  # Iter to find difference in index between value and prefix/unit

        # Value formatted to given precision
        fval = format(float(val[-1]), '.{}f'.format(p))
        print(fval)

        unit_found = False
        prefix_found = False

        try:
            if n[m.start() + 1]:  # Will throw IndexError if no unit was given
                # Identify number of whitespace between value and unit/prefix
                while n[m.start() + i] == ' ':
                    i += 1
                # Assuming a prefix is only one character long
                given_prefix = n[m.start() + i]

                # See if given prefix matches any in dict.
                # Special handling for 'm'due to 'milli' and 'meter' conflict.
                for s, l in _prefixes_phonetic.items():
                    if given_prefix == s and not given_prefix == 'm':
                        read_prefix = l
                        print('Prefix found: {}'.format(s.strip()))
                        prefix_found = True

                    if given_prefix == s and given_prefix == 'm':
                        try:
                            # Throws IndexError if no index after found m
                            if not n[m.start() + i + 1] == ' ':
                                read_prefix = l
                                print('Prefix found: milli')
                                prefix_found = True
                        except IndexError:
                            read_unit = ' Meter'
                            if not unit_found:
                                print('Unit found: Meter')
                                unit_found = True

                if prefix_found:
                    # Prefix found means there is something following
                    unit = n[m.start() + i + 1:]
                    # Anything following our prefix
                    for s, l in _units_phonetic.items():
                        if unit == s:
                            read_unit = l
                            print('Unit found: {}'.format(s.strip()))
                            unit_found = True
                    if not unit_found:
                        print('Unit not found: {}'.format(unit))

                elif not unit_found:  # No matching prefix, no unit found yet
                    print('Prefix not found: {}'.format(given_prefix))
                    unit = n[m.start() + i:]
                    for s, l in _units_phonetic.items():
                        if unit == s:
                            read_unit = l
                            print('Unit found: ' + l)
                            unit_found = True

                if not prefix_found and not unit_found:
                    print('Unit not found: {}'.format(unit))

        except IndexError:
            # Gets thrown when there's nothing following the last digit
            print('No unit.')
            read_line = fval
            # engine.say(read_line)

        except AttributeError:
            print('Empty string')

        if unit_found:
            if prefix_found:
                read_line = fval + read_prefix + read_unit
            else:
                read_line = fval + read_unit

        self.talk(self, read_line)

    def talk(self, talk_string):
        pythoncom.CoInitialize()
        engine = pyttsx3.init()
        engine.say(talk_string)
        engine.runAndWait()
        engine.stop()

    def toggle_adv_settings(self, event):
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

    def on_close(self, event):
        pub.unsubscribe(self.gather_data, 'serial.data')
        mod_refs = list(
            filter(lambda m: m.startswith('modules.multimeter'), sys.modules))
        for mr in mod_refs:
            del sys.modules[mr]
        event.Skip()


def dispose():
    m.Close()


if __name__ == '__main__':
    app = wx.App()
    m = Multimeter(None, 'Plotter settings')
    app.MainLoop()
else:
    m = Multimeter(None, 'Plotter settings')
