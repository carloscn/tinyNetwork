# -*- coding: utf-8 -*-
import sys
import socket
import threading
from PyQt5 import QtCore
from PyQt5.QtCore import QByteArray

class TcpAgent(threading):

    # MACROS
    MODE_CLIENT = 0
    MODE_SERVER = 1
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
    sig_tcp_agent_send_msg = QtCore.pyqtSignal( object )
    sig_tcp_agent_recv_network_msg = QtCore.pyqtSignal( object )

    def __init__(self):
        k = 1

    def set_mode(self,mode):
        self.mode = mode

    def connect(self,ip,port):
        self.tcp_info["ip"] = ip
        self.tcp_info["port"] = port
        if self.mode == self.MODE_SERVER:
            self.tcp_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.tcp_socket.setblocking( False )
            try:
                self.tcp_socket.bind( '', int( self.tcp_info["port"] )  )
            except Exception as ret:
                msg = "Please confirm the port number if occupied.\n"
                self.sig_tcp_agent_send_msg.emit( msg )
            else:
                self.tcp_socket.listen()
        elif self.mode == self.MODE_CLIENT:
            self.tcp_socket.connect( self.tcp_info["ip"], int( self.tcp_info["port"] ) )
        self.is_connect = True


    def disconnect(self):
        self.tcp_socket.close()
        self.is_connect = False

    def send_bytes(self, byteList):
        self.tcp_socket.send( byteList, len(byteList) )

    def send_byte(self, byte):
        self.tcp_socket.send( byte, 1 )

    def run(self):
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




