# -*- coding: latin-1 -*-

#/*                          Part of SERIAL COMMANDER
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

from PyQt4.QtCore import QObject, pyqtSignal
from threading import Thread
import zmq


class Client(QObject):

    new_message = pyqtSignal(str)

    def __init__(self, server="localhost", send_port="5557", recv_port="5556"):
        QObject.__init__(self)
        self.context = zmq.Context()

        #Sender socket using PULL-PUSH pattern
        self.sender_socket = self.context.socket(zmq.PUSH)
        self.sender_socket.connect("tcp://{0}:{1}".format(server, send_port))

        #Start receiver thread
        args = (self.context, server, recv_port)
        self.recv_thread = Thread(target=self.receive, args=args)
        self.recv_thread.daemon = True
        self.recv_thread.start()

    def send(self, message):
        self.sender_socket.send(message.encode())

    def receive(self, context, server, port):
        #Receiver socket using SUB_PUB pattern
        receiver_socket = context.socket(zmq.SUB)
        receiver_socket.connect("tcp://{0}:{1}".format(server, port))
        receiver_socket.setsockopt(zmq.SUBSCRIBE, b"")

        while True:
            #Get the publisher's message
            message = receiver_socket.recv()
            self.new_message.emit(str(message))
