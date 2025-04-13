import time
import json
import threading

from queue import Queue

from pubsub import pub

import meshtastic
import meshtastic.serial_interface

from meshtastic import LOCAL_ADDR
from meshtastic.util import message_to_json


class FMeshNetwork:
    def __init__(self, fmesh):
        self.fmesh = fmesh

        self.interface = None
        self.local_node = None
        self.connected = False

    def connect(self, device=None):
        "Connecting to the radio device"

        if not device:
            device = self.fmesh.config.get("FMESH_DEVICE", None)

        if not device:
            self.fmesh.messages.put(f"[ERROR] Radio device not set...")
            return

        self.connect_thread = threading.Thread(
            name="connect",
            target=self.init_meshtastic,
            args=(device,),
        )
        self.connect_thread.start()
        self.fmesh.messages.put(f"[RADIO] Connecting to device {device}")

    ###
    # meshtastic interface

    def init_meshtastic(self, device):
        "Connecting meshtastic and the radio"

        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")

        self.interface = meshtastic.serial_interface.SerialInterface(device)

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        "called when we (re)connect to the radio"

        if not self.connected:
            self.fmesh.messages.put("[RADIO] Meshtastic connected")

            # self.interface.showInfo()
            # self.interface.showNodes()

            self.local_node = self.interface.getNode(LOCAL_ADDR)
            self.connected = True

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

            self.fmesh.messages.put(decoded)
            # self.fmesh.messages.put("[RECEIVED] " + str(decoded["portnum"]))
        except:
            self.fmesh.messages.put("[ERROR] Packet: " + str(packet)[:90])

    def get_channel_name(self, index):
        try:
            channel = self.local_node.getChannelByChannelIndex(index)
            name = channel.settings.name
            if channel.role == 1 and name == "":
                name = "Default"
            return name
        except:
            return None

    ###
    # sending messages

    def send_text(self, raw, channel_id=0):
        # self.fmesh.messages.put("[SEND RAW] Sending raw: " + raw)
        self.interface.sendText(raw, channelIndex=channel_id)
        # self.fmesh.messages.put("[SEND RAW] Raw sent: " + raw)

    def send_raw_bytes(raw):
        self.fmesh.messages.put("[SEND RAW BYTES] Sending raw: " + raw)
        self.interface.sendBytes(raw)
        self.fmesh.messages.put("[SEND RAW BYTES] Raw sent: " + raw)
