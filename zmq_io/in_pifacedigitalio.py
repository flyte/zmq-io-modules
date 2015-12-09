import argparse
import json
from datetime import datetime

import pifacedigitalio as pfdio
from twisted.internet import reactor
from txzmq import ZmqEndpoint, ZmqFactory, ZmqPullConnection


gpio = pfdio.PiFaceDigital()


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("pull_uri")
    return p.parse_args()


def handle_input(msg):
    """
    Called when a ZeroMQ PULL message is received.
    """
    print "Received input at %s" % datetime.now()
    try:
        msg = json.loads(msg[0])
    except ValueError as e:
        print "Message was not JSON formatted, discarding: %s" % e
        return
    for pin, value in msg.items():
        print "Setting output pin %s to %s" % (pin, value)
        try:
            gpio.output_pins[int(pin)].value = int(value)
        except KeyError:
            print "No output pin with index of %s" % pin
        except ValueError:
            print "Output pin values must evaluate to integers, not %s" % value


if __name__ == "__main__":
    args = parse_args()
    zf = ZmqFactory()
    e = ZmqEndpoint("bind", args.pull_uri)
    s = ZmqPullConnection(zf, e)
    s.onPull = handle_input
    reactor.run()
