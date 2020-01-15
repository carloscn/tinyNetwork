# -*- coding: utf-8 -*-
import sys
import subprocess
import MainUi
import socket
from TcpAgent import TcpAgent as tcpAgent
from TcpAgent import UdpAgent as udpAgent
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QMessageBox
from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtCore


''' BACKUP SLOT FUNCTIONS ON MainUi.py to avoid MainUi.py is re-write when converted to MainUi.py automatilly.

        self.pushButtonConnect.clicked.connect(MainWindow.on_pushButtonConnect_click)
        self.comboBoxProtocal.currentIndexChanged['int'].connect(MainWindow.on_comboBoxProtocal_currentIndexChanged)
        self.comboBoxMode.currentIndexChanged['int'].connect(MainWindow.on_comboBoxMode_currentIndexChanged)
        self.pushButtonPing.clicked.connect(MainWindow.on_pushButtonPing_click)
        self.pushButtonDisconnect.clicked.connect(MainWindow.on_pushButtonDisconnect_click)
        self.radioButtonRecASCII.clicked['bool'].connect(MainWindow.on_radioButtonRecASCII_clicked)
        self.radioButtonRecHex.toggled['bool'].connect(MainWindow.on_radioButtonRecHex_clicked)
        self.checkBoxWordWrap.clicked['bool'].connect(MainWindow.on_checkBoxWordWrap_clicked)
        self.checkBoxDisplayTime.clicked['bool'].connect(MainWindow.on_checkBoxDisplayTime_clicked)
        self.checkBoxDisplayRecTime.clicked['bool'].connect(MainWindow.on_checkBoxDisplayRecTime_clicked)
        self.radioButtonSendASCII.clicked['bool'].connect(MainWindow.on_radioButtonSendASCII_checked)
        self.radioButtonSendHex.clicked['bool'].connect(MainWindow.on_radioButtonSendHex_checked)
        self.checkBoxRepeatSend.clicked['bool'].connect(MainWindow.on_radioButtonRepeatSend_checked)
        self.spinBox.valueChanged['int'].connect(MainWindow.on_spinBoxTime_valueChanged)
        self.pushButtonSend.clicked['bool'].connect(MainWindow.on_pushButtonSend_clicked)
        self.pushButtonClear.clicked['bool'].connect(MainWindow.on_pushButtonClear_clicked)
        self.pushButtonWriteIp.clicked.connect(MainWindow.on_pushButtonWriteIp_clicked)
        self.pushButtonAppIp.clicked.connect(MainWindow.on_pushButtonAppIp_clicked)
'''


class MainWindow(QMainWindow):

    ui = MainUi.Ui_MainWindow()
    # UI MACROS
    MODE_SERVER = 0
    MODE_CLIENT = 1
    tcp_mode = MODE_CLIENT
    PROTOCAL_TCP = 0
    PROTOCAL_UDP = 1
    protocal_mode = PROTOCAL_TCP
    tcpAgent = tcpAgent()

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.ui.setupUi(self)
        self.init_ui_logic()
        self.tcpAgent.sig_tcp_agent_send_msg.connect( self.on_tcpAgent_send_msg )


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
        self.ui.lineEditAimIp.setText("192.168.31.1")
        self.ui.lineEditLocalPort.setText( "8388" )
        self.ui.lineEditLocalIp.setText( self.get_local_ip() )
        self.ui.comboBoxMode.setCurrentIndex( self.tcp_mode )
        self.ui.comboBoxProtocal.setCurrentIndex( self.protocal_mode )

    def pop_error_window(self, content):
        error_win = QMessageBox()
        error_win.setModal( True )
        error_win.setWindowTitle( "Error" )
        error_win.setIcon(QMessageBox.Critical)
        error_win.setText( content )
        error_win.exec()

    def pop_info_window(self, content):
        info_win = QMessageBox()
        info_win.setModal( True )
        info_win.setWindowTitle( "Info" )
        info_win.setIcon(QMessageBox.Information)
        info_win.setText( content )
        info_win.exec()

    @QtCore.pyqtSlot("int", name="on_comboboxprotocal_currentindexchanged")
    def on_comboBoxProtocal_currentIndexChanged(self, int_index):
        print("ui: protocal index change to " + str( int_index ) )
        self.protocal_mode = int_index
        if int_index == self.PROTOCAL_UDP:
            self.ui.comboBoxMode.setEnabled( False )
            self.ui.pushButtonConnect.setEnabled( False )
            self.ui.pushButtonDisconnect.setEnabled( False )
        else:
            self.ui.comboBoxMode.setEnabled( True )
            self.ui.pushButtonConnect.setEnabled( True )
            self.ui.pushButtonDisconnect.setEnabled( True )

    @QtCore.pyqtSlot("int", name="on_comboboxmode_currentindexchanged")
    def on_comboBoxMode_currentIndexChanged(self, int_index):
        self.tcp_mode = int_index
        if self.tcp_mode == self.MODE_SERVER:
            self.ui.pushButtonConnect.setText("Listen")
        elif self.tcp_mode == self.MODE_CLIENT:
            self.ui.pushButtonConnect.setText("Connect")


    @QtCore.pyqtSlot(name="on_pushbuttonping_click")
    def on_pushButtonPing_click(self):
        aim_ip = self.ui.lineEditAimIp.text()
        self.ui.statusbar.showMessage("ping " + aim_ip + "| waitting...")
        ret = subprocess.call(["ping", aim_ip ,"-c", "2"])
        if ret == 0:
            self.ui.statusbar.showMessage("system: ping " + aim_ip + " network normal.", 3000)
            self.pop_info_window("system: ping " + aim_ip + " network normal." )
        else:
            self.ui.statusbar.showMessage("system: ping " + aim_ip + " network failed.", 3000)
            self.pop_error_window("system: ping " + aim_ip + " network failed.")

    @QtCore.pyqtSlot(name="on_pushbuttonconnect_click")
    def on_pushButtonConnect_click(self):
        if len( self.ui.lineEditLocalIp.text() ) == 0:
            self.pop_error_window("Local IP is Empty!")
            self.ui.lineEditLocalIp.setFocus()
            return
        if len( self.ui.lineEditLocalPort.text() ) == 0:
            self.pop_error_window("Listen Port is Empty!")
            self.ui.lineEditLocalPort.setFocus()
            return
        local_ip = self.ui.lineEditLocalIp.text()
        local_port = int( self.ui.lineEditLocalPort.text() )
        mode = self.ui.comboBoxMode.currentIndex()
        self.tcpAgent.set_mode( mode )
        if  self.tcpAgent.connect( local_ip, local_port ):
            # tcpAgent error information via the msg sginal-slot mechanism
            print( local_ip + "  " + str(local_port) + " error")
            pass
        else:
            self.pop_info_window( local_ip + "  " + str(local_port)  + " has been set up.")

    @QtCore.pyqtSlot(name="on_pushbuttondisconnect_click")
    def on_pushButtonDisconnect_click(self):
        k = 1

    @QtCore.pyqtSlot(name="on_radiobuttonrecascii_clicked")
    def on_radioButtonRecASCII_clicked(self):
        k = 1

    @QtCore.pyqtSlot(name="on_radiobuttonrechex_clicked")
    def on_radioButtonRecHex_clicked(self):
        k = 1

    @QtCore.pyqtSlot(name="on_checkboxwordwrap_clicked")
    def on_checkBoxWordWrap_clicked(self):
        k = 1

    @QtCore.pyqtSlot("bool", name="on_checkboxwordwrap_clicked")
    def on_checkBoxDisplayTime_clicked(self, checked):
        k = 1

    def on_checkBoxDisplayRecTime_clicked(self, checked):
        k = 1

    def on_radioButtonSendASCII_checked(self ,checked):
        k = 1

    def on_radioButtonSendHex_checked(self, checked):
        k = 1

    def on_radioButtonRepeatSend_checked(self, checked):
        k = 1

    def on_spinBoxTime_valueChanged(self, time):
        k = 1

    def on_pushButtonSend_clicked(self, click):
        k = 1

    def on_pushButtonClear_clicked(self, click):
        k = 1

    def on_pushButtonWriteIp_clicked(self):
        k = 1

    def on_pushButtonAppIp_clicked(self):
        k = 1

    def on_tcpAgent_send_msg(self, msg):
        self.pop_error_window( msg )


if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())