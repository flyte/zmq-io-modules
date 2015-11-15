import io
import argparse
import cPickle as pickle
import subprocess as sp

import zmq
from PIL import Image

from io_gphoto2_pb2 import Photo


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("req_uri", help="ZeroMQ bind uri on which to receive REQ commands from")
    p.add_argument("--gphoto2", help="Location of gphoto2 binary", default="/usr/bin/gphoto2")
    return p.parse_args()


def take_photo():
    """
    Take a photo and return an instance of `io_gphoto2_pb2.Photo`.
    """
    sp.call((
        "%s" % args.gphoto2,
        "--capture-image-and-download",
        "--force-overwrite",
        "--filename=output.jpg"
    ))
    with open("output.jpg") as f:
        img = Image.open(f)
        size_x, size_y = img.size
        return Photo(
            bytes=f.read(),
            size_x=size_x,
            size_y=size_y,
            mode=img.mode
        )


if __name__ == "__main__":
    args = parse_args()

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(args.req_uri)

    while True:
        msg = socket.recv().strip()
        if msg == "take_photo":
            print "Taking photo.."
            socket.send(str(take_photo().SerializeToString()))
        else:
            print "Didn't recognise command: %s" % msg
