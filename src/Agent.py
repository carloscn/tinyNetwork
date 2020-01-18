# -*- coding: utf-8 -*-
import sys
import socket
import threading
import inspect
import ctypes
import signal
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray, QObject, pyqtSignal

class UdpAgent(threading.Thread):
    def __init__(self):
        k = 1

class TcpAgent(QObject):

    # MACROS
    MODE_CLIENT = 1
    MODE_SERVER = 0
    mode = MODE_SERVER
    # threading info
    threading_id = 178
    threading_name = "tcp_rec"
    threading_counter = 0
    # class need
    is_connect = False;
    tcp_socket =  socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    tcp_info = {
        "ip":"0.0.0.0",
        "port":"45"
    }
    client_socket_list = list()
    # information signal channel.
    sig_tcp_agent_send_msg = pyqtSignal(str, name="sig_tcp_agent_send_msg")
    sig_tcp_agent_recv_network_msg = pyqtSignal("QByteArray", name="sig_tcp_agent_recv_network_msg")

    # int: 0 a client exit; str is empty
    # int: 1 a client connected in; str is name and port eg: "192.168.1.1,58853"
    sig_tcp_agent_client_name = pyqtSignal(int, str, name="sig_tcp_agent_client_name")

    def __init__(self):
        super( TcpAgent, self ).__init__()

    def _async_raise(self, tid, exctype):
        """raises the exception, performs cleanup if needed"""
        tid = ctypes.c_long(tid)
        if not inspect.isclass(exctype):
            exctype = type(exctype)
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
        if res == 0:
            raise ValueError("invalid thread id")
        elif res != 1:
            # """if it returns a number greater than one, you're in trouble,
            # and you should call it again with exc=NULL to revert the effect"""
            ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
            raise SystemError("PyThreadState_SetAsyncExc failed")

    def stop_thread(self, thread):
        self._async_raise(thread.ident, SystemExit)

    def set_mode(self,mode):
        self.mode = mode

    def run_thread(self):
        if self.is_connect != True:
            return
        if self.mode == self.MODE_SERVER:
            while True:
                try:
                    client_socket, client_address = self.tcp_socket.accept()
                except Exception as ret:
                    pass
                else:
                    self.client_socket_list.append( (client_socket, client_address) )
                    client_info = str( client_address )
                    client_socket.setblocking( False )
                    msg = "TCP address: " + client_address
                    self.sig_tcp_agent_send_msg( msg )
                for client, address in self.client_socket_list:
                    try:
                        recv_tcp_msg = client.recv( 1024 )
                    except Exception as ret:
                        pass
                    else:
                        if recv_tcp_msg:
                            q_recv_array = QByteArray()
                            q_recv_array.append( recv_tcp_msg )
                            self.sig_tcp_agent_recv_network_msg.emit( q_recv_array )
                        else:
                            client.close()
                            self.client_socket_list.remove( (client, address) )

        elif self.mode == self.MODE_CLIENT:
            while True:
                try:
                    recv_tcp_msg = self.tcp_socket.recv(1024)
                except Exception as ret:
                    pass
                else:
                    if recv_tcp_msg:
                        q_recv_array = QByteArray()
                        q_recv_array.append(recv_tcp_msg)
                        self.sig_tcp_agent_recv_network_msg.emit(q_recv_array)

    recv_threading = threading.Thread()
    def connect(self,ip, port):
        self.tcp_info["ip"] = ip
        self.tcp_info["port"] = port
        if self.mode == self.MODE_SERVER:
            # tcp_socket needs to reassign using the socket.socket, otherwise,
            # an [Errno 9] Bad file descriptor error will occur.
            # Tcp client connects to the Service-Terminal with a new port number.
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.setblocking( False )
            try:
                self.tcp_socket.bind( ( ip, port ) )
            except Exception as ret:
                msg = "Please confirm the port number if occupied.\n"
                self.sig_tcp_agent_send_msg.emit( str(ret) + msg )
                self.is_connect = False
            else:
                self.tcp_socket.listen()
                self.is_connect = True
                self.recv_threading = threading.Thread(target=self.run_thread, name = self.threading_name)
                self.recv_threading.start()
        elif self.mode == self.MODE_CLIENT:
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.tcp_socket.connect( (ip, port) )
            except Exception as ret:
                msg = "\nPlease confirm that the host is listening.\n"
                self.sig_tcp_agent_send_msg.emit( str(ret) + msg )
                self.is_connect = False
            else:
                self.is_connect = True
                self.recv_threading = threading.Thread(target=self.run_thread, name=self.threading_name)
                self.recv_threading.start()
            return self.is_connect
        self.tcp_socket.close()
        self.is_connect = False
        return self.is_connect

    def send_bytes(self, byteList):
        try :
            self.tcp_socket.sendall( byteList )
        except Exception as ret:
            msg = "The network run into an error!\n" + str( ret )
            self.sig_tcp_agent_send_msg.emit( msg )
        else:
            pass

    def send_byte(self, byte):
        self.tcp_socket.send( byte, 1 )

    def tcp_disconnect(self):
        self.is_connect = False
        print("system: kill recv thread.")
        self.stop_thread(self.recv_threading)
        print("system: closed tcp socket.")
        self.tcp_socket.shutdown(2)
        self.tcp_socket.close()