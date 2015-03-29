import zmq
import sys
import threading
import argparse


print_stderr = lambda msg: sys.stderr.write("%s\n" % msg)


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("pub_uri", help="ZeroMQ bind uri on which to publish std "
        "input using ZeroMQ PUB.")
    p.add_argument("pull_uri", help="ZeroMQ bind uri from which to PULL "
        "messages to print on stdout.")
    p.add_argument("--pub_prefix", default="STDIN", help="Prefix to add to me"
        "ssages published over ZeroMQ.")
    return p.parse_args()


def set_up_pub_socket(uri):
    """
    Create ZeroMQ PUB socket and bind it to the specified uri.
    """
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(uri)
    return socket


def zmq_to_stdout(uri, stop_event):
    """
    Create ZeroMQ PULL socket, bind it to the specified uri, then write any
    messages received to stdout. Close the port and return when stop_event is
    set.
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
        sys.stdout.write(msg)
        sys.stdout.flush()
    pull.close()


if __name__ == "__main__":
    args = parse_args()
    pub = set_up_pub_socket(args.pub_uri)

    stop_event = threading.Event()
    z2s = threading.Thread(
        target=zmq_to_stdout, args=(args.pull_uri, stop_event))
    z2s.start()

    try:
        print_stderr("Ready for input")
        while True:
            msg = raw_input()
            print "Sending %s" % msg
            pub.send_unicode(unicode(args.pub_prefix + msg))
    except KeyboardInterrupt:
        print_stderr("") # Newline
    finally:
        stop_event.set()
        print_stderr("Waiting for threads to finish..")
        z2s.join()
        print_stderr("Closing ZMQ socket..")
        pub.close()
        print_stderr("Bye!")
