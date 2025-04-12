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

        self.serial_port = None

        self.beacon_on = False
        # Is set to false on GUI mode so that we can control the beaconing
        self.beaconing_priority_settings = True

        self.bnum = 0

        self.localNode = None

        self.is_connected = False

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
        "called when a packet arrives"

        try:
            decoded = packet["decoded"]

            decoded["from"] = packet["from"]
            decoded["to"] = packet["to"]

            try:
                decoded["channel"] = packet["channel"]
            except:
                decoded["channel"] = 0

            decoded["channel_name"] = self.get_channel_name(decoded["channel"])

            self.fmesh.messages_log.put(decoded)
            self.fmesh.main_log.put("[RECEIVED] Packet: " + str(decoded["portnum"]))
        except:
            self.fmesh.main_log.put("[ERROR] Packet: " + str(packet)[:90])

    def on_connection(self, interface, topic=pub.AUTO_TOPIC):
        # called when we (re)connect to the radio
        if not self.is_connected:
            self.fmesh.main_log.put("[RADIO] Connection established, starting to listen for packets...")

            self.is_connected = True
            # self.interface.showInfo()
            # self.interface.showNodes()
            self.localNode = self.interface.getNode(LOCAL_ADDR)

    # INFO Monitor and, if applicable, start beaconing using encrypted messages or plaintext messages

    def check_beacon(self):
        # NOTE As the scenarios can include long range radios, we have low bandwidth.
        # By waiting N seconds between beacons, we ensure that we are not beaconing
        # too often and spamming the radio channel with beacons.
        if self.beacon_on:
            self.fmesh.main_log.put("[MAIN CYCLE] Checking for beacon cooldown...")

            # The following keeps the code running while we cooldown beaconing too
            if (self.beacon_cooldown > 0):
                if not self.cooldown_header:
                    self.fmesh.main_log.put("+++ COOLDOWN ACTIVE +++")
                    self.cooldown_header = True

                if self.beacon_cooldown % 10 == 0:
                    self.fmesh.main_log.put(f"[MAIN CYCLE] Beacon cooldown: {str(self.beacon_cooldown)}")

                self.beacon_cooldown -= 1
            else:
                self.fmesh.main_log.put("*** COOLDOWN COMPLETE ***")
                self.fmesh.main_log.put("[MAIN CYCLE] Beaconing is activated, proceeding...")
                self.beacon_cooldown = int(os.getenv('BEACONING_INTERVAL'))
                self.send_beacon()
                self.fmesh.main_log.put("[MAIN CYCLE] Beacon emitted. Proceeding to the next cycle...")
        else:
            #self.fmesh.main_log.put("[MAIN CYCLE] Beaconing is not activated, proceeding...")
            pass

    def send_beacon(self, encrypted=False):
        # If we are supposed to be beaconing, we need to send a beacon and wait 10 seconds
        self.fmesh.main_log.put("[BEACONING] Sending beacon...")

        # NOTE Generating a beacon first
        self.bnum += 1
        beacon = {
            "type": "beacon",
            "number": self.bnum,
            "timestamp": int(time.time()),
            "info": self.interface.getShortName(),
        }

        self.interface.sendText(json.dumps(beacon))
        self.fmesh.main_log.put("[BEACONING] Beacon sent: " + json.dumps(beacon))

    def send_raw(self, raw, channel_id=0):
        self.fmesh.main_log.put("[SEND RAW] Sending raw: " + raw)
        self.interface.sendText(raw, channelIndex=channel_id)
        self.fmesh.main_log.put("[SEND RAW] Raw sent: " + raw)

    def send_raw_bytes(raw):
        self.fmesh.main_log.put("[SEND RAW BYTES] Sending raw: " + raw)
        self.interface.sendBytes(raw)
        self.fmesh.main_log.put("[SEND RAW BYTES] Raw sent: " + raw)

    def connect(self, serial_port=None):
        self.serial_port = serial_port

        # Connecting to the radio
        pub.subscribe(self.on_receive, "meshtastic.receive")
        pub.subscribe(self.on_connection, "meshtastic.connection.established")

        self.interface = meshtastic.serial_interface.SerialInterface(self.serial_port)
        self.fmesh.main_log.put("[RADIO] Opening serial connection")

    def listSerials(self):
        # TODO
        pass


