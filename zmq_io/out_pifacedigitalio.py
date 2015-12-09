import argparse
import json

import pifacedigitalio as pfdio
import zmq


PINS = (
    0b00000001,
    0b00000010,
    0b00000100,
    0b00001000,
    0b00010000,
    0b00100000,
    0b01000000,
    0b10000000
)


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("pub_uri")
    p.add_argument("--prefix", default="INPUT")
    return p.parse_args()


def set_up_pub_socket(uri):
    """
    Create ZeroMQ PUB socket and bind it to the specified uri.
    """
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(uri)
    return socket


def input_changed(event):
    """
    Handler for input changes. Forms a dictionary containing event information and PUBlishes it
    using the global ZeroMQ PUB socket.
    """
    input_port = event.chip.input_port.value
    data = {
        "state": {i: bool(input_port & PINS[i]) for i, _ in enumerate(PINS)}
    }
    socket.send("%s%s" % (args.prefix, json.dumps(data)))


if __name__ == "__main__":
    args = parse_args()
    socket = set_up_pub_socket(args.pub_uri)
    listener = pfdio.InputEventListener()
    for i, _ in enumerate(PINS):
        listener.register(i, pfdio.IODIR_BOTH, input_changed)
    listener.activate()
