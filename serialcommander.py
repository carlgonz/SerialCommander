#!/usr/bin/env python
# -*- coding: latin-1 -*-

#/*                          SERIAL COMMANDER
#*                A simple serial interface to send commands
#*
#*      Copyright 2013, Carlos Gonzalez Cortes, carlgonz@ug.uchile.cl
#*
#* This program is free software: you can redistribute it and/or modify
#* it under the terms of the GNU General Public License as published by
#* the Free Software Foundation, either version 3 of the License, or
#* (at your option) any later version.
#*
#* This program is distributed in the hope that it will be useful,
#* but WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#* GNU General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with this program.  If not, see <http://www.gnu.org/licenses/>.
#*/

import sys
import datetime
import json

from PyQt4.Qt import *
from PyQt4 import QtGui
from PyQt4 import QtCore

from forms.SerialCommander_UI import Ui_MainWindow
from forms.EditCommandDialog_UI import Ui_DialogEditCommandList

from client import Client


class SerialCommander(QtGui.QMainWindow):
    """
    Main class, creates and configures main window. Also sets signals and
    slots.
    """
    #Señales
    _new_char = pyqtSignal(type(""))  # New char signal
    
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

        #Instance variables
        self.client = None
        self.alive = False
        self.receiver_thread = None
        self.history = []
        self.history_cnt = 0
        self.timestamp = False
        self.put_timestamp = True

        #Load config
        try:
            config_file = open("config/config.json", 'r')
            self.config = json.load(config_file)
            config_file.close()
        except IOError:
            self.config = {}

        self.commands_list = self.config.get("commands", [])
                
        #Set GUI
        self.window = Ui_MainWindow()
        self.window.setupUi(self)
        self.setup_comm()
        self.setup_send()
        self.setup_actions()
        
    def setup_comm(self):
        """
        Sets connections combobox.
        """
        #Connections
        self.window.pushButtonOpenPort.clicked.connect(self.open_connection)
        self.window.pushButtonClosePort.clicked.connect(self.close_connection)

        #Hosts
        available_hosts = self.config.get("hosts", ["", ])
        self.window.lineEditURL.setText(available_hosts[0])

        #Ports
        available_ports = self.config.get("ports", ["", ])
        available_ports.reverse()
        self.window.comboBoxPortRecv.addItems(available_ports)
        self.window.comboBoxPortSend.addItems(available_ports)

    def setup_send(self):
        """
        Config cmd send and selection window
        """
        #Add command list
        self.window.listWidgetCommand.addItems(self.commands_list)
        
        #Conexiones
        self.window.listWidgetCommand.itemDoubleClicked.connect(self.command_clicked)
        self.window.pushButtonSend.clicked.connect(self.send_msg)
        self.window.checkBoxTimestamp.toggled.connect(self.timestamp_toggle)
    
    def timestamp_toggle(self, value):
        """
        Slot que intercambia entre agregar o no la marca de tiempo
        """
        self.timestamp = value
    
    def setup_actions(self):
        """
        Configura los menus de la barra de herramientas
        """
        self.window.actionGuardar.triggered.connect(self.save_log)
        self.window.actionAgregar_comando.triggered.connect(self.add_cmd)
        # self.client.new_message.connect(self.write_terminal)
        
    def add_cmd(self):
        """
        Edita la lista de comandos
        """
        dialog = EditCommandDialog(self,self.commands_list)
        self.commands_list = dialog.run_tool()
        
        self.window.listWidgetCommand.clear()
        self.window.listWidgetCommand.addItems(self.commands_list)
    
    def write_terminal(self, text):
        """
        Escribe el texto en el widget de lectura, configura el
        cursor hasta el final de cocumento y agrega marca de tiempo
        """
        
        text = text.replace('\r', '')
        
        #Moves cursor to end
        c = self.window.textEditTerminal.textCursor()
        c.movePosition(QTextCursor.End)
        self.window.textEditTerminal.setTextCursor(c)
        
        if self.timestamp:
            #Modo Timestamp, busca nueva linea para agregar timestamp
            if self.put_timestamp:
                #Agregar la marca de tiempo si corresponde
                ts = datetime.datetime.now().isoformat(' ')
                ts = '\n[{0}] '.format(ts)
                self.window.textEditTerminal.insertPlainText(ts)
                self.put_timestamp = False
            
            #Buscar si hay nueva linea para agregar marca despues
            lines = text.split('\n',1)
            text = lines[0]
            self.window.textEditTerminal.insertPlainText(text)
            
            #Seguir procesando el resto de la linea
            if len(lines) > 1:
                self.put_timestamp = True
                if lines[1] != '':
                    self.write_terminal(lines[1])
                    
        else:
            #Normal mode, just write text in terminal
            self.window.textEditTerminal.insertPlainText(text)
                    
    def command_clicked(self,item):
        """
        Mueve un comando de la lista, a la salida de texto
        """
        self.window.lineEditSend.setText(item.text())
        
    def open_connection(self):
        """
        Opens connection with server indicated in GUI
        """
        self.window.pushButtonClosePort.setEnabled(True)
        self.window.pushButtonOpenPort.setEnabled(False)
        self.window.pushButtonSend.setEnabled(True)

        url_server = self.window.lineEditURL.text()
        recv_port = self.window.comboBoxPortRecv.currentText()
        send_port = self.window.comboBoxPortSend.currentText()

        try:
            self.client = Client(url_server, send_port, recv_port)
            self.client.new_message.connect(self.write_terminal)
            self.alive = True
        except Exception as e:
            QMessageBox.critical(self, 'Error', 'Error al abrir el puerto serial\n'+str(e))
            self.close_connection()
        
    def close_connection(self):
        """
        Close connections
        """
        self.window.pushButtonClosePort.setEnabled(False)
        self.window.pushButtonOpenPort.setEnabled(True)
        self.window.pushButtonSend.setEnabled(False)
        self.alive = False
        self.client = None

    def send_msg(self):
        """
        Send written message to server
        """
        msg = str(self.window.lineEditSend.text())
        self.addHistory(msg)
        
        #Agregar LF y/o CR
        if self.window.checkBoxLF.isChecked():
            msg += '\n'
        if self.window.checkBoxCR.isChecked():
            msg += '\r'
        
        self.client.send(msg)
        self.window.lineEditSend.clear()
        self.history_cnt = 0
        
    def save_log(self):
        """
        Saves terminal content to file
        """
        doc_file = QFileDialog.getSaveFileName(self, "Guardar archivo", QDir.currentPath(), "Archivos de texto (*.txt);;All files (*.*)")
        doc_file = str(doc_file)
        document = self.window.textEditTerminal.document()
        m_write = QTextDocumentWriter()
        m_write.setFileName(doc_file)
        m_write.setFormat("txt")
        m_write.write(document)
            
    def addHistory(self, line):
        """
        Agrega una nueva linea al historial. Elimina entradas antiguas si supera
        cierta cantidad de mensajes.
        """
        if len(self.history) > 100:
            self.history.pop()
        
        try:
            if not (line == self.history[-1]):
                self.history.append(line)
        except:
            self.history.append(line)
            
    def getHistory(self, index):
        """
        Retorna el elemendo numero index del historial
        """
        if index > 0 and index <= len(self.history):
            return self.history[-index]
        else:
            return ''
    
    def historySend(self):
        """
        Agrega una linea del historial para ser enviada
        """
        if self.history_cnt >= 0:
            if self.history_cnt > len(self.history):
                self.history_cnt = len(self.history)
                
            text = self.getHistory(self.history_cnt)
            self.window.lineEditSend.setText(text)
        else:
            self.history_cnt = 0                
            
    def closeEvent(self, event):
        """
        Cierra la aplicacion correctamente. Cerrar los puertos, detener thread
        y guardar la lista de comandos creada
        """
        if self.alive:
            self.close_connection()
        # file_cmd = open(self.commands_file, 'w')
        # for line in self.commands_list:
        #     file_cmd.write(line+'\n')
        # file_cmd.close()
        event.accept()
        
    def keyPressEvent(self, event):
        """
        Maneja eventos asociados a teclas presionadas
        """
        if event.key() == QtCore.Qt.Key_Up:
            if self.window.lineEditSend.hasFocus():
                self.history_cnt+=1
                self.historySend()
        
        if event.key() == QtCore.Qt.Key_Down:
            if self.window.lineEditSend.hasFocus():
                self.history_cnt-=1
                self.historySend()
            
        event.accept()
        
            
class EditCommandDialog(QtGui.QDialog):
    """
    Herramienta para edicion de comandos
    """
    def __init__(self,parent=None,cmd_list=[]):
        
        QtGui.QDialog.__init__(self,parent)
        
        self.ventana = Ui_DialogEditCommandList()
        self.ventana.setupUi(self)
        
        self.cmd_list = cmd_list
        self.ventana.listWidgetCommand.addItems(self.cmd_list)
        
        #Conexiones
        self.ventana.pushButtonDelete.clicked.connect(self.delete_item)
        self.ventana.pushButtonAdd.clicked.connect(self.add_item)
        
    def run_tool(self):
        """
        Abre el dialogo para que el usuario la lista. Al cerrar, recupera
        los cambios y retorna la nueva lista
        """
        ret = super(EditCommandDialog, self).exec_()
        
        if(ret):
            self.cmd_list = []
            for row in range(self.ventana.listWidgetCommand.count()):
                item = self.ventana.listWidgetCommand.item(row)
                self.cmd_list.append(item.text())
         
        return self.cmd_list
    
    def delete_item(self):
        """
        Borra los item seleccionados
        """
        for item in self.ventana.listWidgetCommand.selectedItems():
            row = self.ventana.listWidgetCommand.row(item)
            witem = item = self.ventana.listWidgetCommand.takeItem(row)
            del witem
            
        
    def add_item(self):
        """
        Agrega un nuevo item 
        """
        cmd = self.ventana.lineEditAdd.text()
        item = self.ventana.listWidgetCommand.addItem(cmd)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = SerialCommander()
    gui.show()
    sys.exit(app.exec_())
