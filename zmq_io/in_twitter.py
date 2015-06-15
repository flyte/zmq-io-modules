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
