import zmq
import argparse
import threading
import json
import pifacedigitalio as pfdio
from time import sleep

IN_PORTS = (
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
    p.add_argument("pull_uri")
    p.add_argument("--pub_prefix", default="GPIO")
    return p.parse_args()


def set_up_pub_socket(uri):
    """
    Create ZeroMQ PUB socket and bind it to the specified uri.
    """
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(uri)
    return socket


def zmq_to_gpio_out(uri, gpio, stop_event):
    """
    Create a ZeroMQ PULL oscket, bind it to the specified uri, then change any
    specified GPIO outputs according to messages received. Close the port and
    return when stop_event is set.
    """
    context = zmq.Context()
    pull = context.socket(zmq.PULL)
    pull.bind(uri)

    while not stop_event.is_set():
        try:
            msg = pull.recv(zmq.NOBLOCK)
        except zmq.error.Again:
            stop_event.wait(0.01)
            continue
        print "Received message: %s" % msg
        _handle_rx_msg(msg, gpio)
    pull.close()


def _handle_rx_msg(msg, gpio):
    """
    Decipher the received message and perform the desired functions on GPIO.
    """
    try:
        msg = json.loads(msg)
    except ValueError as e:
        print "Message was not JSON formatted, discarding: %s" % e
        return
    for pin, value in msg.items():
        try:
            gpio.output_pins[int(pin)].value = 1 if value else 0
        except KeyError:
            print "No output pin with index of %s" % pin
        except ValueError:
            print "Output pins must be numbers, not %s" % pin


if __name__ == "__main__":
    args = parse_args()
    gpio = pfdio.PiFaceDigital()
    pub = set_up_pub_socket(args.pub_uri)

    stop_event = threading.Event()
    z2gpio = threading.Thread(
        target=zmq_to_gpio_out, args=(args.pull_uri, gpio, stop_event))
    z2gpio.start()

    current_values = {}
    try:
        while True:
            port = gpio.input_port.value
            values = {i: bool(port & IN_PORTS[i]) for i in range(0,8)}
            if values != current_values:
                pub.send_unicode(
                    u"%s%s" % (args.pub_prefix, json.dumps(values)))
                current_values = values
            sleep(0.01)
    except KeyboardInterrupt:
        pass
    finally:
        stop_event.set()
        print "Waiting for threads to finish ..."
        z2gpio.join()
        print "Closing ZMQ socket ..."
        pub.close()
        print "Bye!"