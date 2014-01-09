#!/usr/bin/env python

import zmq

# Socket to broadcast messages
context = zmq.Context()
socket = context.socket(zmq.PUB)
socket.bind("tcp://*:5556")

# Socket to receive messages on
receiver = context.socket(zmq.PULL)
receiver.bind("tcp://*:5557")

while True:
    # Wait for next request from client
    message = receiver.recv()
    # Broadcast message to all subscribers
    socket.send(message)
