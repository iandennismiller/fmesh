import time
import json

from queue import Queue

from pubsub import pub

import meshtastic
import meshtastic.serial_interface

from meshtastic import LOCAL_ADDR
from meshtastic.util import message_to_json

from .keys import FMeshKeys


class FMeshNetwork:
    def __init__(self, fmesh):
        self.fmesh = fmesh

        # Ensuring we have an identity
        self.keys = FMeshKeys(fmesh)

        self.interface = None

        self.local_node = None

        self.is_connected = False

        # self.beacon = FMeshBeacon(fmesh)

    def connect(self, serial_port=None):
        "Connecting to the radio"

        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")

        self.interface = meshtastic.serial_interface.SerialInterface(serial_port)

    def get_channel_name(self, index):
        try:
            chan = self.local_node.getChannelByChannelIndex(index)
            name = chan.settings.name
            if chan.role == 1 and name == "":
                name = "Default"
            return name
        except:
            return None

    ###
    # event callbacks

    def on_receive(self, packet):
        "called when a packet arrives"

        try:
            decoded = packet["decoded"]
            decoded["from"] = packet["from"]
            decoded["to"] = packet["to"]

            try:
                decoded["channel"] = int(packet["channel"])
            except:
                decoded["channel"] = 0

            decoded["channel_name"] = self.get_channel_name(decoded["channel"])

            self.fmesh.messages_log.put(decoded)
            self.fmesh.main_log.put("[RECEIVED] " + str(decoded["portnum"]))
        except:
            self.fmesh.main_log.put("[ERROR] Packet: " + str(packet)[:90])

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        "called when we (re)connect to the radio"

        if not self.is_connected:
            self.fmesh.main_log.put("[RADIO] Connection established, starting to listen for packets...")

            # self.interface.showInfo()
            # self.interface.showNodes()

            self.local_node = self.interface.getNode(LOCAL_ADDR)
            self.is_connected = True

    ###
    # sending messages

    def send_raw(self, raw, channel_id=0):
        self.fmesh.main_log.put("[SEND RAW] Sending raw: " + raw)
        self.interface.sendText(raw, channelIndex=channel_id)
        self.fmesh.main_log.put("[SEND RAW] Raw sent: " + raw)

    def send_raw_bytes(raw):
        self.fmesh.main_log.put("[SEND RAW BYTES] Sending raw: " + raw)
        self.interface.sendBytes(raw)
        self.fmesh.main_log.put("[SEND RAW BYTES] Raw sent: " + raw)
