import time
import json

from pubsub import pub

import meshtastic
import meshtastic.serial_interface

from meshtastic import LOCAL_ADDR
from meshtastic.util import message_to_json

from .keys import MeshKeys


class MeshNetwork:
    def __init__(self):
        # Ensuring we have an identity
        self.keys = MeshKeys()

        self.interface = None

        self.serial_port = None

        self.beacon_on = False
        # Is set to false on GUI mode so that we can control the beaconing
        self.beaconing_priority_settings = True

        self.bnum = 0

        self.localNode = None

        self.channelNames = []

        self.connected = False

        self.msg_received = []

    def get_channel_name(self, index):
        try:
            chan = self.localNode.getChannelByChannelIndex(index)
            name = chan.settings.name
            if chan.role == 1 and name == "":
                name = "Default"
            return name
        except:
            return None

    def on_receive(self, packet):
        print("[RECEIVED] Received packet: " + str(packet))

        # called when a packet arrives
        try:
            decoded = packet["decoded"]
            decoded["from"] = packet["from"]
            decoded["to"] = packet["to"]

            channel = 0

            try:
                channel = packet["channel"]
            except:
                pass

            decoded["channel"] = channel
            decoded["channel_name"] = get_channel_name(channel)
        except:
            print("[ERROR] Could not decode packet: discarding it")
            return
            # ANCHOR We have received a packet and we decoded it

        print("--- decoded ---\n", decoded, "\n---")

        # Let's take the type of the packet
        packet_type = decoded["portnum"]
        print("Received packet type: " + packet_type)

        self.msg_received.append(decoded)

    def on_connection(self, topic=pub.AUTO_TOPIC):
        # called when we (re)connect to the radio
        # defaults to broadcast, specify a destination ID if you wish
        self.connected = True
        self.interface.showInfo()
        self.interface.showNodes()

        # theName = json.dumps(self.interface.getShortName())
        self.localNode = self.interface.getNode(LOCAL_ADDR)

        print(repr(self.localNode.channels))

        for i in range(8):
            print(i, self.get_channel_name(i))

        print("----------------------")

    # INFO Monitor and, if applicable, start beaconing using encrypted messages or plaintext messages

    def beacon(self, encrypted=False):
        # If we are supposed to be beaconing, we need to send a beacon and wait 10 seconds
        print("[BEACONING] Sending beacon...")

        # NOTE Generating a beacon first
        self.bnum += 1
        beacon = {
            "type": "beacon",
            "number": self.bnum,
            "timestamp": int(time.time()),
            "info": self.interface.getShortName(),
        }

        self.interface.sendText(json.dumps(beacon))
        print("[BEACONING] Beacon sent: " + json.dumps(beacon))

    def send_raw(self, raw, channel_id=0):
        print("[SEND RAW] Sending raw: " + raw)
        self.interface.sendText(raw, channelIndex=channel_id)
        print("[SEND RAW] Raw sent: " + raw)

    def send_raw_bytes(raw):
        print("[SEND RAW BYTES] Sending raw: " + raw)
        self.interface.sendBytes(raw)
        print("[SEND RAW BYTES] Raw sent: " + raw)

    def connect(self, serial_port=None):
        self.serial_port = serial_port

        # Connecting to the radio
        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")

        self.interface = meshtastic.serial_interface.SerialInterface(self.serial_port)
        print("[INITIALIZATION] Connection to radio established")

    def listSerials(self):
        # TODO
        pass


