import traceback
import argparse
import threading
import Queue as queue
from importlib import import_module

import zerorpc


class LightingServer:

    def __init__(self, states, state_queue, change_event, quit_event):
        self.states = states
        self.state_queue = state_queue
        self.change_event = change_event
        self.quit_event = quit_event

    def _clear_queue(self):
        try:
            self.state_queue.get_nowait()
        except queue.Empty:
            pass

    def run_states(self, state_names):
        """
        Clear the existing queue and run a new list of states.
        """
        if not all(hasattr(states, state) for state in state_names):
            raise ValueError("All states must exist.")
        self._clear_queue()
        for state in state_names:
            self.state_queue.put(getattr(states, state))
        self.change_event.set()

    def run_state(self, state_name):
        """
        Clear the existing queue and run a single state.
        """
        self.run_states((state_name,))

    def list_states(self):
        """
        Get a list of all valid states.
        """
        return filter(lambda x: not x.startswith("_"), dir(self.states))

    def stop_state(self, clear_queue=True):
        """
        Stop the currently running state. Clears the queue by default, otherwise will
        skip to the next state in the queue.
        """
        if clear_queue:
            self._clear_queue()
        self.change_event.set()


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
    p.add_argument("uri", help="URI for ZeroRPC server to bind to")
    p.add_argument(
        "states_module",
        help="Python module containing lighting states as functions")
    args = p.parse_args()

    states = import_module(args.states_module)
    change_event = threading.Event()
    quit_event = threading.Event()
    state_queue = queue.Queue()

    s = zerorpc.Server(LightingServer(states, state_queue, change_event, quit_event))
    s.bind(args.uri)

    t_lighting = threading.Thread(
        target=lighting_loop, args=(state_queue, change_event, quit_event))
    t_lighting.start()

    try:
        s.run()
    except KeyboardInterrupt:
        print ""
    finally:
        print "Stopping lighting thread.."
        quit_event.set()
        change_event.set()
        if t_lighting is not None:
            t_lighting.join()
        print "Bye!"
