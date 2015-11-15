import os
import io
import argparse
import cPickle as pickle
import subprocess as sp

import zerorpc


class GPhoto2API:

    def take_photo(self):
        """
        Take a photo and return a dict containing the image and metadata.
        """
        try:
            sp.call((
                "%s" % args.gphoto2,
                "--capture-image-and-download",
                "--force-overwrite",
                "--filename=output.jpg"
            ))
            with open("output.jpg", "rb") as f:
                return dict(
                    bytes=f.read(),
                    ext="jpg"
                )
        finally:
            try:
                os.unlink("output.jpg")
            except OSError:
                pass


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("req_uri", help="ZeroMQ bind uri on which to receive REQ commands from")
    p.add_argument("--gphoto2", help="Location of gphoto2 binary", default="/usr/bin/gphoto2")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    s = zerorpc.Server(GPhoto2API())
    s.bind(args.req_uri)
    s.run()
