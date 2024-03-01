#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import sys

from yocto_api import YAPI, YSensor, YRefParam
from yocto_serialport import YSerialPort
from yocto_colorledcluster import YColorLedCluster

ledColors = [ 0 ] * 512
values = [ 0, 0, 0 ]
colors = [ 0, 0, 0 ]

def dmxCallback(fct, measure):
    idx = fct.get_userData()
    val = int(measure.get_averageValue() / 4)
    if idx == 0:
        for i in range(0,3):
            colors[i] = val << (8*i)
    else:
        values[idx-1] = val
        print("\b\b\b\b\b\b\b\b\b\b\b{:2d} {:2d} {:2d}".format(values[2], values[1], values[0]), end='')
    for x in range(0, 64):
        ofs = 8 * x
        for y in range(0, 3):
            if x < values[y]:
                ledColors[ofs + 3 * y + 0] = colors[y]
                ledColors[ofs + 3 * y + 1] = colors[y]
            else:
                ledColors[ofs + 3 * y + 0] = 0
                ledColors[ofs + 3 * y + 1] = 0

def logfun(line):
    print('LOG : ' + line.rstrip())

# setup the API to use local USB devices + external YoctoHub-Ethernet
errmsg = YRefParam()
YAPI.RegisterLogFunction(logfun)
if YAPI.RegisterHub("usb", errmsg) != YAPI.SUCCESS:
    sys.exit("RegisterHub error: " + errmsg.value)
if YAPI.RegisterHub("192.168.1.61", errmsg) != YAPI.SUCCESS:
    sys.exit("RegisterHub error: " + errmsg.value)

# locate Yoctopuce devices
dmxPortIn = YSerialPort.FindSerialPort("DMX-IN.serialPort")
if not dmxPortIn.isOnline():
    sys.exit("No Yocto-RS485-V2 with logical name DMX-IN found")
leds = YColorLedCluster.FirstColorLedCluster()
if leds is None:
    sys.exit("No Yocto-Color-V2 found")

# configure Yocto-RS485-V2 interface for DMX512 standard
dmxPortIn.set_voltageLevel(YSerialPort.VOLTAGELEVEL_RS485)
dmxPortIn.set_protocol("Frame:2ms")
dmxPortIn.set_serialMode("250000,8N2")

# bind callback to first four genericSensors
for idx in range(0, 4):
    slider = YSensor.FindSensor("DMX-IN.genericSensor"+str(idx+1))
    slider.set_userData(3-idx)
    slider.set_reportFrequency("25/s")
    slider.registerTimedReportCallback(dmxCallback)

print('************  DMX512 input demo - hit Ctrl-C to Stop ')

while True:
    YAPI.Sleep(40, errmsg)
    leds.set_rgbColorArray(0, ledColors)