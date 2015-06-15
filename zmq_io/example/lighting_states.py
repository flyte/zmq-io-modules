from time import sleep
from raspledstrip.ledstrip import *
from raspledstrip import animation

ZERO_TO_ONE_100 = [x/100.0 for x in range(0, 101)]
ONE_TO_ZERO_100 = [x/100.0 for x in range(100, -1, -1)]

led = LEDStrip(32, True)
led.setMasterBrightness(1)
colour = Color(0, 0, 0)

def _fade_in(col):
    global colour
    for i in ZERO_TO_ONE_100:
        colour = Color(col.r, col.g, col.b, i)
        led.fill(colour)
        led.update()


def _fade_out():
    global colour
    for i in ONE_TO_ZERO_100:
        colour = Color(colour.r, colour.g, colour.b, i)
        led.fill(colour)
        led.update()


def rainbow(change_event):
    print "rainbow started"
    ani = animation.RainbowCycle(led)
    while not change_event.isSet():
        ani.step()
        led.update()
    print "rainbow stopping"


def white(change_event):
    print "white started"
    _fade_in(Color(255, 255, 255))
    print "white stopping"


def scan(change_event):
    print "scan start"
    ani = animation.LarsonScanner(led, Color(255, 255, 255))
    while not change_event.isSet():
        ani.step()
        led.update()
        change_event.wait(0.01)
    print "scan stop"


def error(change_event):
    print "error start"
    for i in range(0, 5):
               led.fillRGB(255, 0, 0)
               led.update()
               change_event.wait(0.2)
               led.fillOff()
               led.update()
               change_event.wait(0.2)
    print "error stop"


def off(change_event):
    print "off start"
    led.all_off()
    print "off stop"
