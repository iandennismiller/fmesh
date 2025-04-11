import time
import json

from hashlib import sha256
from pubsub import pub

import meshtastic
import meshtastic.serial_interface
from meshtastic import LOCAL_ADDR
from meshtastic.util import message_to_json

import fmesh.keys as keys


serial_port = None
interface = None

beaconOn = False
# Is set to false on GUI mode so that we can control the beaconing
beaconingPrioritySettings = True

bnum = 0

connected = False

msg_received = []

localNode = None
channelNames = []

def getChannelName(index):
    global localNode
    try:
        chan = localNode.getChannelByChannelIndex(index)
        name = chan.settings.name
        if chan.role == 1 and name == "":
            name = "Default"
        return name
    except:
        return None

# NOTE Just an easy wrapper around sha256
def hash(input):
    return sha256(input.encode('utf-8')).hexdigest()


def onReceive(packet, interface):
    global msg_received
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
        decoded["channel_name"] = getChannelName(channel)
    except:
        print("[ERROR] Could not decode packet: discarding it")
        return
        # ANCHOR We have received a packet and we decoded it
    print("--- decoded ---\n", decoded, "\n---")
    # Let's take the type of the packet
    packet_type = decoded["portnum"]
    print("Received packet type: " + packet_type)
    msg_received.append(decoded)


def onConnection(interface, topic=pub.AUTO_TOPIC):
    global connected, localNode
    # called when we (re)connect to the radio
    # defaults to broadcast, specify a destination ID if you wish
    connected = True
    theName = json.dumps(interface.getShortName())
    interface.showInfo()
    interface.showNodes()
    #print(repr(interface.getMyNodeInfo()))
    localNode = interface.getNode(LOCAL_ADDR)
    print(repr(localNode.channels))
    for i in range(8):
        print(i, getChannelName(i))
    print("----------------------")
    #interface.sendText(theName + " greets you!")

# INFO Monitor and, if applicable, start beaconing using encrypted messages or plaintext messages


def beacon(encrypted=False):
    # If we are supposed to be beaconing, we need to send a beacon and wait 10 seconds
    print("[BEACONING] Sending beacon...")
    # NOTE Generating a beacon first
    our_info = interface.getShortName()
    our_timestamp = int(time.time())
    global bnum
    bnum += 1
    beacon = {
        "type": "beacon",
        "number": bnum,
        "timestamp": our_timestamp,
        "info": our_info
    }
    interface.sendText(json.dumps(beacon))
    print("[BEACONING] Beacon sent: " + json.dumps(beacon))


def sendRaw(raw, channel_id=0):
    print("[SEND RAW] Sending raw: " + raw)
    interface.sendText(raw, channelIndex = channel_id) # babor
    print("[SEND RAW] Raw sent: " + raw)


def sendRawBytes(raw):
    print("[SEND RAW BYTES] Sending raw: " + raw)
    interface.sendBytes(raw)
    print("[SEND RAW BYTES] Raw sent: " + raw)


def connect(serialPort=None):
    global serial_port
    global interface
    # Ensuring we have an identity
    keys.ensure()
    # Connecting to the radio
    serial_port = serialPort
    pub.subscribe(onReceive, "meshtastic.receive")
    pub.subscribe(onConnection, "meshtastic.connection.established")
    interface = meshtastic.serial_interface.SerialInterface(serial_port)
    print("[INITIALIZATION] Connection to radio established")


def listSerials():
    # TODO
    pass
