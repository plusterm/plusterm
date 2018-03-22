from wx.lib.pubsub import pub
import sys


def handle_data(data):
	print(data)


def on_untick():
	pub.unsubscribe(handle_data, 'serial.data')

pub.subscribe(handle_data, 'serial.data')