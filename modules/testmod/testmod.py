from wx.lib.pubsub import pub
import sys


def handle_data(data):
    m = 'rs'
    pub.sendMessage('module.send', data=m)


def on_untick():
    pub.unsubscribe(handle_data, 'serial.data')


pub.subscribe(handle_data, 'serial.data')