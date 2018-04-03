import queue
import serial
import time
import re
import socket
from wx.lib.pubsub import pub
from serial.tools import list_ports
from com_reader import ComReaderThread

class Communicator():
    """ Handles all external comunication """

    def __init__(self,context):
        self.threadq = queue.Queue()
        self.errorq = queue.Queue()
        self.ser = None
        self.readerthread = None
        self.connection_type = None
        self.socket = None
        self.context = context


    def connect(self, **settings):
        try:
            if settings['type'] == 'serial':
                self.connection_type = 'serial'
                self.ser = serial.Serial()

                self.ser.port = settings['port']
                self.ser.baudrate = settings['baudrate']
                self.ser.stopbits = settings['stopbits']
                self.ser.parity = settings['parity']
                self.ser.bytesize = settings['bytesize']
                self.ser.timeout = 0.1
            
                self.ser.open()
    
                if self.readerthread is not None:
                    if not self.readerthread.isAlive():
                        self.readerthread = ComReaderThread(self.ser, self.threadq, self.errorq)
                        self.readerthread.start()
    
                else:
                    self.readerthread = ComReaderThread(self.ser, self.threadq, self.errorq)
                    self.readerthread.start()

                return True

            elif settings['type'] == 'socket':
                self.connection_type = 'socket'
                self.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((settings['host'], int(settings['port'])))
                self.socket.settimeout(0.01)
                return True

        except Exception as e:
            ts = time.time()
            self.errorq.put((ts, str(e)))
            return False

    
    def disconnect(self):
        """ stops/close all threads and streams """
        if self.connection_type == 'serial':
            try:
                self.readerthread.stop(0.01)
                self.ser.close()
                self.connection_type = None
                return True

            except Exception as e:
                ts = time.time()
                self.errorq.put((ts, e))
                return False

        if self.connection_type == 'socket':
            self.socket.close()
            self.connection_type = None
            return True
            

    def send_cmd(self, cmd):
        """ send a command to the ser assuming it is a string
        """
        if self.ser is not None and self.connection_type == 'serial':
            self.ser.write(cmd.encode())

        if self.socket is not None and self.connection_type == 'socket':
            cmd += '\n'
            self.socket.sendall(cmd.encode())


    def get_data(self):
        """ get the data """
        if self.connection_type == 'serial':
            return self.threadq.get(False)

        if self.connection_type == 'socket':
            try:
                res = self.socket.recv(2056)
                if not res:
                    return

                t = time.time()
                return (t, res)

            except socket.timeout:
                pass

            except Exception as e:
                self.context.disconnect_serial()
                t = time.time()
                self.errorq.put((t, str(e) + '\n'))


    def get_error(self):
        return self.errorq.get(False)
    
    
def getPorts():
    # lists all the available serial devices connected to the computer
    port_list = list_ports.comports()
    ports = [port.device for port in port_list]
    return sorted(ports)


