ZMQ IO Modules
==============

This is a collection of runnable Python modules which communicate using ZeroMQ (0mq) and either perform actions when receiving 0mq messages, send 0mq messages when actions are performed, or both.

The modules are prefixed with in/out/io to identify whether they are an input/output/both type of module.

The Modules
-----------

#### io_stdio

Handles standard input and output. This means that you can type into the console and your message will be published over 0mq. Messages received over 0mq will be printed to standard output.

#### out_states

Imports a Python module and upon reception of a 0mq message, will run the specified function within it. This is useful for setting lighting states for example.

##### states.py

    def print_hi_loads(change_event):
        while not change_event.isSet():
            print "Hi!"
            change_event.wait(1)

    def count_up(change_event):
        i = 0
        while not change_event.isSet():
            i += 1
            print i
            change_event.wait(1)

    def print_hello_world(change_event):
        print "Hello, World!"

##### Example 0mq input

    count_up

Send just the function name to set that state. Send another function name to switch to another one.

#### io_pifacedigitalio

Publishes a message over 0mq describing the pifacedigitalio input port states every time one changes. Changes the pifacedigitalio output states when a message is received over 0mq.

##### Example 0mq output

    {
        "0": false,
        "1": true,
        "2": false,
        "3": false,
        "4": false,
        "5": true,
        "6": false,
        "7": false
    }

##### Example 0mq input

    {
        "2": true,
        "5": false
    }

#### in_lirc

Publishes the button code over 0mq when LIRC receives a button press on an infrared receiver.