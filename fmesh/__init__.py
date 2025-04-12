import threading

from queue import Queue

from dotenv import dotenv_values

from .network import FMeshNetwork
from .keys import FMeshKeys


class FMesh:
    def __init__(self):
        "INFO Initializing FMesh structure"

        self.messages = Queue()

        self.messages.put("[SYSTEM] Starting FMesh...")

        self.config = dotenv_values(".env")
        self.halt = threading.Event()

        self.keys = FMeshKeys(self)
        self.mesh_network = FMeshNetwork(self)

        self.messages.put("[SYSTEM] Connecting to Meshtastic")
        self.mesh_network.connect()

        # self.beacon = FMeshBeacon(fmesh)

        self.messages.put("[SYSTEM] FMesh Initialized")
