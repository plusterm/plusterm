import wx
from wx.lib.pubsub import pub
import importlib
import queue
import sys

import gui
import communicator

class SerialMonitor(wx.App):
	''' Entry point and central class ('context') for Plusterm '''
	def __init__(self):	
		super(SerialMonitor, self).__init__()
		self.communicator = communicator.Communicator(self)	


	def OnInit(self):
		# Start the GUI
		self.sm_gui = gui.SerialMonitorGUI(None, title='Plusterm', context=self)
		self.sm_gui.Show()
		self.SetTopWindow(self.sm_gui)
		return True


	def OnExit(self):
		if self.communicator.comstream is not None:
			self.disconnect_serial()


	def connect_serial(self, port, baudrate):
		if self.communicator.connect(port=port, baudrate=baudrate):
			self.log_to_gui('Port opened\n')
			return True
		return False


	def disconnect_serial(self):
		if self.communicator.disconnect():
			self.log_to_gui('Port closed\n')
			return True
		return False
		

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
	SM.MainLoop()

if __name__ == '__main__':
	main()