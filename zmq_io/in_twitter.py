import twitter
import argparse
from time import sleep
from ConfigParser import SafeConfigParser

CONFIG_SECTION = "twitter"


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
    p = argparse.ArgumentParser()
    p.add_argument("track", help="The keyword to filter tweets by")
    p.add_argument("--config_path", default="twitter.ini")
    args = p.parse_args()

    api = twitter.Api(**load_config(args.config_path))
    creds = api.VerifyCredentials()
    print "You are logged in as %s from %s" % (creds.name, creds.location)

    stream = api.GetStreamFilter(track=args.track.split(","))
    print "Now streaming tweets with the keyword '%s'.." % args.track
    watch_stream(stream)
