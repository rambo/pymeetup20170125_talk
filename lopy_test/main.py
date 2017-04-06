from network import LoRa
import time
import binascii
import socket
import pycom 
import struct 

# Disable heartbeat
pycom.heartbeat(False)
pycom.rgbled(0x000000)


APP_EUI = 'AD A4 DA E3 AC 12 67 6B'
from config import  APP_KEY

class connectionmanager:
    def __init__(self):
            self.lora = LoRa(mode=LoRa.LORAWAN,  adr=True)
            self.lora.power_mode(LoRa.ALWAYS_ON)
            print("Hello world!")
            print("My LoRa device ID is %s" % binascii.hexlify(self.lora.mac())) 
            app_eui = binascii.unhexlify(APP_EUI.replace(' ',''))
            app_key = binascii.unhexlify(APP_KEY.replace(' ',''))
            self.lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)

            # TODO: make into coroutine (or thread)
            # wait until the module has joined the network
            while not self.lora.has_joined():
                time.sleep(2.5)
                print("Waiting to join...")

            print("Network joined!")
            self.s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

    def run(self):
        self.s.setblocking(False)
        self.s.send('I am alive!')
        last_uplink = time.time()
        while True:
            msg = self.s.recv(64)
            if msg:
                print("Got message %s" % repr(msg))
                pycom.rgbled(struct.unpack('<i', binascii.unhexlify(msg))[0])
            if time.time() - last_uplink > 60:
                print("time is {}, sending uplink".format(time.time()))
                self.s.setblocking(True)
                self.s.send('Still alive! {}'.format(time.time()))
                self.s.setblocking(False)
                last_uplink = time.time()
            else:
                time.sleep(0.1)


c = connectionmanager()
c.run()
