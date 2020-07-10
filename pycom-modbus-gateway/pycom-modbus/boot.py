from network import WLAN
from network import Server
import os
import time
import pycom
import micropython


micropython.alloc_emergency_exception_buf(100)

pycom.heartbeat(False)


print('===  Generic Modbus TCP - v1.0 ===')

wlan = WLAN()
wlan.deinit()

#pybytes.disconnect()

pycom.rgbled(0xff0000)
print('Booted')
