import traceback
import zmq
import argparse
import threading
import Queue as queue
from time import sleep
from importlib import import_module


def lighting_loop(state_queue, change_event, quit_event):
    while not quit_event.isSet():
        try:
            state = state_queue.get(timeout=0.1)
            change_event.clear()
            state(change_event)
        except queue.Empty:
            pass
        except Exception:
            print traceback.format_exc()


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("listen_uri", help="ZeroMQ uri for PULL socket to bind to")
    p.add_argument(
        "states_module",
        help="Python module containing lighting states as functions")
    args = p.parse_args()

    states = import_module(args.states_module)
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    receiver.bind(args.listen_uri)

    change_event = threading.Event()
    quit_event = threading.Event()
    state_queue = queue.Queue()
    state = None
    new_state = None

    t_lighting = threading.Thread(
        target=lighting_loop, args=(state_queue, change_event, quit_event))
    t_lighting.start()

    try:
        while True:
            msg = receiver.recv().lower()

            chain = msg.split(",")
            if not all([hasattr(states, state) for state in chain]):
                continue

            # Clear queue
            while True:
                try:
                    state_queue.get_nowait()
                except queue.Empty:
                    break

            # Create new queue
            for state in chain:
                state_queue.put(getattr(states, state))

            # Kick it off
            change_event.set()

    except KeyboardInterrupt:
        print ""
    finally:
        print "Stopping lighting thread.."
        change_event.set()
        quit_event.set()
        if t_lighting is not None:
            t_lighting.join()
        print "Bye!"