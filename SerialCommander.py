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
import threading
import time
import datetime
import serial
from serial.tools.list_ports import comports as listports
from serial.tools.list_ports import grep as listports_grep

from PyQt4.Qt import *
from PyQt4 import QtGui
from PyQt4 import QtCore

from forms.SerialCommander_UI import Ui_MainWindow
from forms.EditCommandDialog_UI import Ui_DialogEditCommandList

class SerialCommander(QtGui.QMainWindow):
    ''' 
    Clase principal, aca se crea y configura la ventana. Tambien contiene
    los slots y conexiones con otras señales
    '''
    #Señales
    _new_char = pyqtSignal(type("")) #Se lee un nuevo char
    
    def __init__(self):
        '''
        Se inicializan la ventana llamando al metodo setupUi y se realizan
        las conexiones señal-slots
        '''
        
        QtGui.QMainWindow.__init__(self)
        
        #Variables de instancia
        self.SerialComm = serial.Serial()
        self.alive = False
        self.receiver_thread = None
        self.commands_file = "config/cmd_list.lst"
        self.commands_list = []
        self.history = []
        self.history_cnt = 0
        self.timestamp = False
        self.put_timestamp = True
                
        #Configurar ventana
        self.ventana = Ui_MainWindow()
        self.ventana.setupUi(self)
        self.setup_comm()
        self.setup_send()
        self.setup_actions()
        
    def setup_comm(self):
        '''
        Configura el combo-box conexiones completando puertos
        y baudrates disponibles
        '''
        
        #Conexiones
        self.ventana.pushButtonOpenPort.clicked.connect(self.open_port)
        self.ventana.pushButtonClosePort.clicked.connect(self.close_port)
        
        #Se agregan los puertos disponibles
        comm_ports = listports()
        comm_ports.reverse()
        for port in comm_ports:
            port_name = port[0]
            self.ventana.comboBoxPorts.addItem(port_name)
        
        #Se agregan los baudrates disponibles
        baudrates = str(serial.Serial.BAUDRATES)[1:-1].split(',')
        self.ventana.comboBoxBaudrate.addItems(baudrates)
        
    def setup_send(self):
        '''
        Configura la ventana de seleccion y envio de comandos
        '''
        #Leer el archivo con la lista de comandos disponibles
        try:
            cmd_file = open(self.commands_file,'r')
            self.commands_list = cmd_file.readlines()
            cmd_file.close()
        except:
            cmd_file = open(self.commands_file,'w')
            cmd_file.close()
       
        #Agregar los comandos a la lista
        for i in range(len(self.commands_list)):
            self.commands_list[i] = self.commands_list[i][:-1]
            
        self.ventana.listWidgetCommand.addItems(self.commands_list)
        
        #Conexiones
        self.ventana.listWidgetCommand.itemDoubleClicked.connect(self.command_clicked)
        self.ventana.pushButtonSend.clicked.connect(self.send_msg)
        self.ventana.checkBoxTimestamp.toggled.connect(self.timestamp_toggle)
    
    def timestamp_toggle(self, value):
        '''
        Slot que intercambia entre agregar o no la marca de tiempo
        '''
        self.timestamp = value
    
    def setup_actions(self):
        '''
        Configura los menus de la barra de herramientas
        '''
        self.ventana.actionGuardar.triggered.connect(self.save_log)
        self.ventana.actionAgregar_comando.triggered.connect(self.add_cmd)
        self._new_char.connect(self.write_terminal)
        
    def add_cmd(self):
        '''
        Edita la lista de comandos
        '''
        dialog = EditCommandDialog(self,self.commands_list)
        self.commands_list = dialog.run_tool()
        
        self.ventana.listWidgetCommand.clear()
        self.ventana.listWidgetCommand.addItems(self.commands_list)
    
    def write_terminal(self, text):
        '''
        Escribe el texto en el widget de lectura, configura el
        cursor hasta el final de cocumento y agrega marca de tiempo
        '''
        
        text = text.replace('\r','')
        
        if self.timestamp:
            #Modo Timestamp, busca nueva linea para agregar timestamp
            if self.put_timestamp:
                #Agregar la marca de tiempo si corresponde
                ts = datetime.datetime.now().isoformat(' ')
                ts = '[{0}] '.format(ts)
                self.ventana.textEditTerminal.insertPlainText(ts)
                self.put_timestamp = False
            
            #Buscar si hay nueva linea para agregar marca despues
            lines = unicode(text).split('\n',1)
            text = lines[0]
            self.ventana.textEditTerminal.insertPlainText(text)
            
            #Seguir procesando el resto de la linea
            if len(lines) > 1:
                self.put_timestamp = True
                if lines[1] != '':
                    self.write_terminal(lines[1])
                else:
                    self.ventana.textEditTerminal.insertPlainText('\n')
        else:
            #Modo normal, solo escribir todo por consola
            self.ventana.textEditTerminal.insertPlainText(text)
        
        #Mover el cursor al final de documento
        c =  self.ventana.textEditTerminal.textCursor()
        c.movePosition(QTextCursor.End)
        self.ventana.textEditTerminal.setTextCursor(c)
        
    def command_clicked(self,item):
        '''
        Mueve un comando de la lista, a la salida de texto
        '''
        self.ventana.lineEditSend.setText(item.text())
        
    def open_port(self):
        '''
        Abre el puerto serial indicado en la GUI
        '''
        self.ventana.pushButtonClosePort.setEnabled(True)
        self.ventana.pushButtonOpenPort.setEnabled(False)
        self.ventana.pushButtonSend.setEnabled(True)
        
        puerto   = self.ventana.comboBoxPorts.currentText()
        baudrate = self.ventana.comboBoxBaudrate.currentText()
        
        self.SerialComm.port = str(puerto)
        self.SerialComm.baudrate = int(baudrate)
        self.SerialComm.timeout = 0.1 #[s]
        self.SerialComm.interCharTimeout = 0.01 #[s]
        
        try:
            self.SerialComm.open()
            self.alive = True
            self.receiver_thread = threading.Thread(target=self.reader)
            self.receiver_thread.setDaemon(True)
            self.receiver_thread.start()
        except Exception, e:
            QMessageBox.critical(self, 'Error', 'Error al abrir el puerto serial\n'+str(e))
            self.close_port()
            
        print self.SerialComm
        
        
    def close_port(self):
        '''
        Cierra la comunicacion serial actual
        '''
        self.ventana.pushButtonClosePort.setEnabled(False)
        self.ventana.pushButtonOpenPort.setEnabled(True)
        #self.ventana.pushButtonSend.setEnabled(False)
        self.alive = False
        self.receiver_thread.join()
        self.SerialComm.close()
    
    def send_msg(self):
        '''
        Envia la linea escrita por el puerto serial
        '''
        msg = str(self.ventana.lineEditSend.text())
        self.addHistory(msg)
        
        #Agregar LF y/o CR
        if(self.ventana.checkBoxLF.isChecked()):
            msg +='\n'
        if(self.ventana.checkBoxCR.isChecked()):
            msg +='\r'
        
        self.SerialComm.write(unicode(msg))
        self.ventana.lineEditSend.clear()
        self.history_cnt = 0
        
    def save_log(self):
        '''
        Guarda el contenido de la ventana de log a un archivo
        '''
        #Ventana crear un archivo
        doc_file = QFileDialog.getOpenFileName(self, "Guardar archivo", QDir.currentPath(), "Archivos de texto (*.txt);;All files (*.*)")
        doc_file = str(doc_file)
        document = self.ventana.textEditTerminal.document()
        m_write = QTextDocumentWriter()
        m_write.setFileName(doc_file)
        m_write.setFormat("txt")
        m_write.write(document)
        
    def reader(self):
        '''
        Lee en un thread los datos seriales y los muestra en pantalla
        '''
        while self.alive:
            try:
                to_read = self.SerialComm.inWaiting()
                if(to_read):
                    data = unicode(self.SerialComm.read(to_read))
                    if len(data) and (not data == '\r'):
                        self._new_char.emit(data)
            
            except UnicodeDecodeError, e:
                #print e
                pass
                    
            except serial.SerialException, e:
                self.alive = False
                raise
            
    def addHistory(self, line):
        '''
        Agrega una nueva linea al historial. Elimina entradas antiguas si supera
        cierta cantidad de mensajes.
        '''
        if len(self.history) > 100:
            self.history.pop()
        
        try:
            if not (line == self.history[-1]):
                self.history.append(line)
        except:
            self.history.append(line)
            
    def getHistory(self, index):
        '''
        Retorna el elemendo numero index del historial
        '''
        if index > 0 and index <= len(self.history):
            return self.history[-index]
        else:
            return ''
    
    def historySend(self):
        '''
        Agrega una linea del historial para ser enviada
        '''
        if self.history_cnt >= 0:
            if self.history_cnt > len(self.history):
                self.history_cnt = len(self.history)
                
            text = self.getHistory(self.history_cnt)
            self.ventana.lineEditSend.setText(text)
        else:
            self.history_cnt = 0                
            
    def closeEvent(self, event):
        '''
        Cierra la aplicacion correctamente. Cerrar los puertos, detener thread
        y guardar la lista de comandos creada
        '''
        if self.alive:
            self.close_port()
        file_cmd = open(self.commands_file,'w')
        for line in self.commands_list:
            file_cmd.write(line+'\n')
        file_cmd.close()
        event.accept()
        
    def keyPressEvent(self, event):
        '''
        Maneja eventos asociados a teclas presionadas
        '''
        if event.key() == QtCore.Qt.Key_Up:
            if self.ventana.lineEditSend.hasFocus():
                self.history_cnt+=1
                self.historySend()
        
        if event.key() == QtCore.Qt.Key_Down:
            if self.ventana.lineEditSend.hasFocus():
                self.history_cnt-=1
                self.historySend()
            
        event.accept()
        
            
class EditCommandDialog(QtGui.QDialog):
    '''
    Herramienta para edicion de comandos
    '''
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
        '''
        Abre el dialogo para que el usuario la lista. Al cerrar, recupera
        los cambios y retorna la nueva lista
        '''
        ret = super(EditCommandDialog, self).exec_()
        
        if(ret):
            self.cmd_list = []
            for row in range(self.ventana.listWidgetCommand.count()):
                item = self.ventana.listWidgetCommand.item(row)
                self.cmd_list.append(item.text())
         
        return self.cmd_list
    
    def delete_item(self):
        '''
        Borra los item seleccionados
        '''
        for item in self.ventana.listWidgetCommand.selectedItems():
            row = self.ventana.listWidgetCommand.row(item)
            witem = item = self.ventana.listWidgetCommand.takeItem(row)
            del witem
            
        
    def add_item(self):
        '''
        Agrega un nuevo item 
        '''
        cmd = self.ventana.lineEditAdd.text()
        item = self.ventana.listWidgetCommand.addItem(cmd)


if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    gui = SerialCommander()
    gui.show()
    sys.exit(app.exec_())
