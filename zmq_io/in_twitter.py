import twitter
import argparse
import zmq
from time import sleep
from ConfigParser import SafeConfigParser

CONFIG_SECTION = "twitter"


def parse_args():
    """
    Specify and parse command line arguments.
    """
    p = argparse.ArgumentParser()
    p.add_argument("pub_uri")
    p.add_argument("track", help="The keyword to filter tweets by")
    p.add_argument("--config_path", default="twitter.ini")
    p.add_argument("--pub_prefix", default="TWEET")
    return p.parse_args()


def watch_stream(stream):
    try:
        for msg in stream:
            if "text" in msg:
                if msg["lang"] == "en":
                    print msg["text"]
            else:
                sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        stream.close()


def load_config(path):
    config = SafeConfigParser()
    config.read(path)
    keys = ("consumer_key", "consumer_secret", "access_token_key", "access_token_secret")
    ret = {}
    for key in keys:
        ret[key] = config.get(CONFIG_SECTION, key)
    return ret


if __name__ == "__main__":
    args = parse_args()

    api = twitter.Api(**load_config(args.config_path))
    creds = api.VerifyCredentials()
    print "You are logged in as %s from %s" % (creds.name, creds.location)

    context = zmq.Context()
    pub = context.socket(zmq.PUB)
    pub.bind(args.pub_uri)

    stream = api.GetStreamFilter(track=args.track.split(","))
    print "Now streaming tweets with the keyword '%s'.." % args.track

    try:
        while True:
            for tweet in stream:
                if "text" in tweet:
                    print "Publishing new tweet:"
                    print tweet["text"]
                    pub.send_string("%s%s" % (args.pub_prefix, tweet["text"]))
                else:
                    sleep(0.1)
    finally:
        stream.close()
