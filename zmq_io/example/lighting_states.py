from time import sleep
from raspledstrip.ledstrip import *
from raspledstrip import animation

led = LEDStrip(32, True)
led.setMasterBrightness(1)


def rainbow(change_event):
    print "rainbow started"
    ani = animation.RainbowCycle(led)
    while not change_event.isSet():
        ani.step()
        led.update()
    print "rainbow stopping"


def white(change_event):
    print "white started"
    led.fillRGB(255,255,255)
    led.update()
    change_event.wait(2)
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

