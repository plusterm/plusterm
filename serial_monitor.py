import wx
from wx.lib.pubsub import pub
import importlib
import queue

import gui
import communicator

class SerialMonitor:
	''' Entry point and central class ('context') for Plusterm '''

	def __init__(self):
		# Start the GUI
		app = wx.App()
		self.sm_gui = gui.SerialMonitorGUI(None, title='Plusterm', context=self)	
		self.communicator = communicator.communicator(self)
		app.MainLoop()		


	def connect_serial(self, port, baudrate):
		if self.communicator.connect(port=port, baudrate=baudrate):
			self.log_to_gui('Port opened\n')


	def disconnect_serial(self):
		if self.communicator.disconnect():
			self.log_to_gui('Port closed\n')


	def send_serial(self, cmd):
		self.communicator.send_cmd(cmd)


	def log_to_gui(self, msg):
		self.sm_gui.output(msg)


	def add_module(self, module):
		mod = importlib.import_module('modules.' + module)


	def get_data(self):
		try:
			data = self.communicator.get_data()
			pub.sendMessage('serial.data', data=data)

		except queue.Empty:
			pass


def main():
	SM = SerialMonitor()

if __name__ == '__main__':
	main()