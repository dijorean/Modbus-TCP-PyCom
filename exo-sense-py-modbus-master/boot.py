from network import WLAN
from network import Server
import os
import time
import pycom
import micropython

micropython.alloc_emergency_exception_buf(100)

pycom.heartbeat(False)

print('=== Exo Sense Py - Modbus TCP - v0.0.1 ===')

wlan = WLAN()
wlan.deinit()

pycom.rgbled(0xff0000)
print('Booted')
