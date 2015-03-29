import argparse
import sys
import zmq
import lirc as liblirc


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("pub_uri")
    p.add_argument("lirc_program_name")
    p.add_argument("--pub_prefix", default="LIRC")
    return p.parse_args()


if __name__ == "__main__":
    args = parse_args()
    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.bind(args.pub_uri)
    liblirc.init(args.lirc_program_name)

    try:
        while True:
            try:
                code = liblirc.nextcode()
                if code:
                    sys.stdout.write("\n%s" % code[0])
                    pub.send_string("%s%s" % (args.pub_prefix, code[0]))
                else:
                    sys.stdout.write(".")
                sys.stdout.flush()
            except KeyboardInterrupt:
                print "Bye!"
                break
    finally:
        liblirc.deinit()

