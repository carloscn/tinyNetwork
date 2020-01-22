# -*- coding: utf-8 -*-
import sys
import socket
import threading
import inspect
import ctypes
import signal
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray, QObject, pyqtSignal

class UdpAgent(QObject):

    # threading info
    threading_id = 179
    threading_name = "udp_rec"
    threading_counter = 0
    target_ip = ""
    target_port = 8080
    local_ip = ""
    local_port = 8888
    udp_socket = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )

    TARGET_MODE = 0
    BROADCAST_MODE = 1

    is_blind = False

    sig_udp_agent_send_msg = pyqtSignal(str, name="sig_udp_agent_send_msg")
    sig_udp_agent_send_error = pyqtSignal(str, name="sig_udp_agent_send_error")
    sig_udp_agent_recv_network_msg = pyqtSignal("QByteArray", name="sig_udp_agent_recv_network_msg")

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

    def run_thread(self):
        while True:
            recv_bytes = self.udp_socket.recv(1024)
            if recv_bytes:
                q_recv_array = QByteArray()
                q_recv_array.append(recv_bytes)
                self.sig_udp_agent_recv_network_msg.emit(q_recv_array)

    recv_threading = threading.Thread()
    def bind_udp(self, ip_str, port_int):
        self.local_ip = ip_str
        self.local_port = port_int
        try:
            self.udp_socket.bind( self.local_ip,  self.local_port )
        except Exception as ret:
            msg = "Run into a error:\n" + str(ret)
            self.sig_udp_agent_send_error.emit(msg)
            self.is_blind = False
        else:
            self.is_blind = True
        return self.is_blind

    def unbind_udp(self):
        try:
            self.udp_socket.close()
        except Exception as ret:
            msg = "Run into a error:\n" + str(ret)
            self.sig_udp_agent_send_error.emit(msg)
        else:
            self.is_blind = False

    def send_bytes(self, byte_list):
        try :
            self.udp_socket.sendall( byte_list )
        except Exception as ret:
            msg = "The network run into an error!\n" + str( ret )
            self.sig_udp_agent_send_error.emit( msg )
        else:
            pass

    def send_byte(self, byte):
        try :
            self.udp_socket.send( byte )
        except Exception as ret:
            msg = "The network run into an error!\n" + str( ret )
            self.sig_udp_agent_send_error.emit( msg )
        else:
            pass

    def on_udp_agent_bind_click(self):
        self.bind_udp()

    def on_udp_agent_unbind_click(self):
        self.unbind_udp()

    def __init__(self):
        pass




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

    listen_ip = "127.0.0.1"
    listen_port = 5555
    tcp_socket =  socket.socket( socket.AF_INET, socket.SOCK_STREAM )
    tcp_info = {
        "ip":"0.0.0.0",
        "port":"45"
    }
    client_socket_list = list()
    # information signal channel.
    sig_tcp_agent_send_msg = pyqtSignal(str, name="sig_tcp_agent_send_msg")
    sig_tcp_agent_send_error = pyqtSignal(str, name="sig_tcp_agent_send_error")
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
        if self.mode == self.MODE_SERVER:
            while True:
                client_socket, addr = self.tcp_socket.accept()
                self.client_socket_list.append( (client_socket, addr ) )
                client_info = str( addr )
                msg = "TCP Client is: " + client_info
                self.sig_tcp_agent_send_msg.emit( msg )
                self.sig_tcp_agent_client_name.emit(1, client_info)
                try:
                    while True:
                        for client, address in self.client_socket_list:
                            recv_tcp_msg = client.recv( 1024 )
                            if recv_tcp_msg:
                                q_recv_array = QByteArray()
                                q_recv_array.append( recv_tcp_msg )
                                self.sig_tcp_agent_recv_network_msg.emit( q_recv_array )
                            else:
                                client.close()
                                self.client_socket_list.remove( (client, address) )
                                self.sig_tcp_agent_client_name.emit(0, str(address))
                                break
                finally:
                    self.tcp_socket.close()

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
        if self.mode == self.MODE_SERVER:
            self.listen_ip = ip
            self.listen_port = port
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            #self.tcp_socket.setblocking( True )
            try:
                self.tcp_socket.bind(('0.0.0.0', self.listen_port))
            except Exception as ret:
                msg = "\nPlease confirm the port number if occupied.\n"
                self.sig_tcp_agent_send_error.emit( str(ret) + msg )
                self.is_connect = False
            else:
                self.tcp_socket.listen(100)
                self.is_connect = True
                self.recv_threading = threading.Thread(target=self.run_thread, name=self.threading_name)
                self.recv_threading.start()
                print("sys: tcp server wait recv data.")

        elif self.mode == self.MODE_CLIENT:
            # tcp_socket needs to reassign using the socket.socket, otherwise,
            # an [Errno 9] Bad file descriptor error will occur.
            # Tcp client connects to the Service-Terminal with a new port number.
            self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.tcp_socket.connect( (ip, port) )
            except Exception as ret:
                msg = "\nPlease confirm that the host is listening.\n"
                self.sig_tcp_agent_send_error.emit( str(ret) + msg )
                self.is_connect = False
            else:
                self.is_connect = True
                self.recv_threading = threading.Thread(target=self.run_thread, name=self.threading_name)
                self.recv_threading.start()
        self.tcp_socket.close()
        return self.is_connect

    def send_bytes(self, byteList):
        if self.mode == self.MODE_CLIENT:
            try :
                self.tcp_socket.sendall( byteList )
            except Exception as ret:
                msg = "The network run into an error!\n" + str( ret )
                self.sig_tcp_agent_send_error.emit( msg )
            else:
                pass
        elif self.mode == self.MODE_SERVER:
            try :
                for client, address in self.client_socket_list:
                    client.sendall( byteList )
            except Exception as ret:
                msg = "The network run into an error!\n" + str( ret )
                self.sig_tcp_agent_send_error.emit( msg )
            else:
                pass
        else:
            pass

    def send_byte(self, byte):
        if self.mode == self.MODE_CLIENT:
            self.tcp_socket.send( byte, 1 )
        else:
            self.tcp_socket.send( byte, 1 )

    def tcp_disconnect(self):

        self.is_connect = False
        print("system: kill recv thread.")
        self.stop_thread(self.recv_threading)
        print("system: closed tcp socket.")
        if self.mode == self.MODE_CLIENT:
            self.tcp_socket.shutdown(2)
            self.tcp_socket.close()
        elif self.mode == self.MODE_SERVER:
            for client, address in self.client_socket_list:
                client.close()
            self.tcp_socket.close()
            self.client_socket_list.clear()

        else:
            pass