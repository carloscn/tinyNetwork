# -*- coding: utf-8 -*-
import sys
import MainUi
import socket
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore

class MainWindow(QMainWindow):

    ui = MainUi.Ui_MainWindow()
    # UI MACROS
    MODE_SERVER = 0
    MODE_CLIENT = 1
    tcp_mode = MODE_SERVER
    PROTOCAL_TCP = 0
    PROTOCAL_UDP = 1
    protocal_mode = PROTOCAL_TCP
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui.setupUi(self)
        self.init_ui_logic()

    def on_btn_click_signal(self):
        k = 1
        #self.ui.label.setText("hello")

    def get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    def init_ui_logic(self):
        self.ui.lineEditLocalPort.setText( "8388" )
        self.ui.lineEditLocalIp.setText( self.get_local_ip() )
        self.ui.comboBoxMode.setCurrentIndex( self.tcp_mode )
        self.ui.comboBoxProtocal.setCurrentIndex( self.protocal_mode )

    def on_lineEditProtocal_currentIndexChanged(self, int_index):
        self.protocal_mode = int_index
        if int_index == self.PROTOCAL_UDP:
            self.ui.comboBoxMode.setEnabled( False )
        else:
            self.ui.comboBoxMode.setEnabled( True )

    def on_lineEditMode_currentIndexChanged(self, int_index):
        self.tcp_mode = int_index

    def on_pushButtonConnect_click(self):
        k = 1

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())