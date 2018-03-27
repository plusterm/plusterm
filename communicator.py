import queue
import serial
import time
import re
import socket
from wx.lib.pubsub import pub
from serial.tools import list_ports
from com_reader import ComReaderThread

class Communicator():
    """ communicator handles all external comunication with comports, server/s or p2p....
        etc...
    """

    def __init__(self,context):
        self.threadq = queue.Queue()
        self.errorq = queue.Queue()
        self.comstream = None
        self.readerthread = None
        self.connection_type = None
        self.socket = None
        self.context = context


    def connect(self, **options):
        try:
            if options['type'] == 'serial':
                self.connection_type = 'serial'
                self.comstream = serial.Serial()

                self.comstream.port = options['port']
                self.comstream.baudrate = options['baudrate']
                self.comstream.stopbits = options['stopbits']
                self.comstream.parity = options['parity']
                self.comstream.bytesize = options['bytesize']
                self.comstream.timeout = 0.1
            
                self.comstream.open()
    
                if self.readerthread is not None:
                    if not self.readerthread.isAlive():
                        self.readerthread = ComReaderThread(self.comstream, self.threadq, self.errorq)
                        self.readerthread.start()
    
                else:
                    self.readerthread = ComReaderThread(self.comstream, self.threadq, self.errorq)
                    self.readerthread.start()

                return True

            elif options['type'] == 'socket':
                self.connection_type = 'socket'
                self.socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((options['host'], int(options['port'])))
                self.socket.settimeout(0.01)
                return True

        except Exception as e:
            ts = time.time()
            self.errorq.put((ts, str(e)))
            return False

    
    def disconnect(self):
        """ stops/close all threads and streams
        """
        if self.connection_type == 'serial':
            try:
                self.readerthread.stop(0.01)
                self.comstream.close()
                self.connection_type = None
                return True

            except Exception as e:
                ts = time.time()
                self.errorq.put((ts, e))
                return False

        if self.connection_type == 'socket':
            self.socket.close()
            return True
            

    def send_cmd(self,cmd):
        """ send a command to the comstream assuming it is a string
        """
        if self.comstream is not None and self.connection_type == 'serial':
            self.comstream.write(cmd.encode())

        if self.socket is not None and self.connection_type == 'socket':
            self.socket.sendall(cmd.encode())


    def get_data(self):
        """ get the data
        """
        if self.connection_type == 'serial':
            return self.threadq.get(False)

        if self.connection_type == 'socket':
            try:
                res = self.socket.recv(1024)
                t = time.time()
                return (t, res)

            except socket.timeout:
                pass

            except ConnectionResetError as e:
                self.socket.close()
                t = time.time()
                res = str(e)
                return (t, res)

            except Exception as e:
                t = time.time()
                self.errorq.put((t, str(e)))


    def get_error(self):
        return self.errorq.get(False)
    
    
def getPorts():
    # lists all the available serial devices connected to the computer
    port_list = list_ports.comports()
    ports = [port.device for port in port_list]
    return sorted(ports)


