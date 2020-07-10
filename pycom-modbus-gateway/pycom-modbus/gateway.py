# main.py
# Gateway
#   A couple of thread, one to check the modbus table and send messages to the
#   nodes and other to receive messages from nodes
#

import os
import socket
import time
import struct
import _thread
import ubinascii

from network import LoRa
from uos import urandom

########################### Variables #######################################
# A basic package header
# B: 1 byte for the deviceId
# B: 1 byte for the pkg size
# B: 1 byte for the messageId
# %ds: Formated string for string
_LORA_PKG_FORMAT = "!BBB%ds"

# A basic ack package
# B: 1 byte for the deviceId
# B: 1 byte for the pkg size
# B: 1 byte for the messageId
# B: 1 byte for the Ok (200) or error messages
_LORA_PKG_ACK_FORMAT = "BBBB"

# This device ID, use different device id for each device
_DEVICE_ID = 0x01
_MAX_ACK_TIME = 5000
_RETRY_COUNT = 3

# Open a Lora Socket, use tx_iq to avoid listening to our own messages
#lora = LoRa(mode=LoRa.LORA, tx_iq=True, frequency=870000000, sf=7)
lora = LoRa(mode=LoRa.LORA, tx_iq=True)
lora_sock = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
lora_sock.setblocking(False)

msg_id = 0
entryChangedByReceive = False
# RGB + Timer, 2 characters each one
lightInfo = '0103'

devEui = ubinascii.hexlify(lora.mac()).decode('ascii')

gateway_devices = [0,0,0,0,0,0,0,0,0,0] # [D1,D2,D3,D4,D5,D6,D7,D8,D9,D10]

# Gateway class
class Gateway():
    """docstring for Gateway."""
    ##################### Functions ###########################################
    # Thread to receive messages from nodes
    def thread_receive(self):
        # global entryChangedByReceive
        # TODO: do a infinite Loop
        while True:
            # Wait for messages from nodes.
            start_time = time.ticks_ms()

            while(not check_ack_time(start_time)):
                recv_ack = lora_sock.recv(256)
                # If a message of the size of the acknoledge message is received
                if (len(recv_ack) == 4):
                    print("SIZE CORRECT")

                    entryChangedByReceive = True

                    # TODO: process the information getting the parameters from message
                    # and modifying the modbus table

                    device_id, pkg_len, recv_msg_id, status = struct.unpack(_LORA_PKG_ACK_FORMAT, recv_ack)
                    if (device_id == _DEVICE_ID and recv_msg_id == msg_id):
                        if (status == 200):
                            # Do some code if your message arrived at the central
                            #return True
                            print("Received ...")
                        else:
                            #return False
                            print("Received failed ...")
                time.sleep_ms(urandom(1)[0] << 2)


    def __init__(self):
        super(Gateway, self).__init__()

        # Initializes receive thread
        #_thread.start_new_thread(thread_receive, ())
        ##################### Initialization #############################
        # TODO: Read memory to get the storage value and set the light parameters
        #       Get IR codes and send it by output pin

    # Method to increase message id and keep in between 1 and 255
    def increase_msg_id(self):
        global msg_id
        msg_id = (msg_id + 1) & 0xFF

    # Method for acknowledge waiting time keep
    def check_ack_time(self, from_time):
        current_time = time.ticks_ms()
        return (current_time - from_time > _MAX_ACK_TIME)

    # Method to send messages
    def send_msg(self, msg):
        print("SEND MSG")
        print(msg)

        global msg_id
        retry = _RETRY_COUNT
        while (retry > 0 and not retry == -1):
            retry -= 1
            pkg = struct.pack(_LORA_PKG_FORMAT % len(msg), _DEVICE_ID, len(msg), msg_id, msg)

            lora_sock.send(pkg)

            time.sleep(0.1)

    # Function to get the deviceId from modbus index
    def get_deviceId_from_modbus_ix(self, idx):
        # TODO: Get deviceId from table
        devId = '70B3D5499585FCA1'
        return devId

    # Function to process changes on modbus
    def process_changes_modbus(self, idx, rgbVal, timerVal):

        # Get dev eui required
        requestDevEui = gateway_devices[idx]

        print("DevEUI: %s - reqDevEui: %s" % devEui % requestDevEui)

        # Check if the device EUI is itself
        if (devEui != requestDevEui):
            # Remote changes. Request for node
            # Create messages
            message = requestDevEui + str(rgbVal).zfill(4) + str(timerVal).zfill(4)

            print("transmitted message = %s" % message)

            # Send messages
            send_msg(message)

            increase_msg_id()

            time.sleep(0.1)
        else:
            print("Local changes in progress ...")

            # TODO: Call thread to change the light and do the timer
            #       Get IR codes and send it by output pin

        return True

    def gateway_destroy(self):
        # Exit thread
        _thread.exit()
