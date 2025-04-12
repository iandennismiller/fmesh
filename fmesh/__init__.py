import threading

from queue import Queue

from dotenv import dotenv_values

from fmesh.network import FMeshNetwork


class FMesh:
    def __init__(self):
        "INFO Initializing FMesh structure"

        self.main_log = Queue()
        self.messages_log = Queue()

        self.main_log.put("[SYSTEM] Starting FMesh...")

        self.config = dotenv_values(".env")
        self.halt = threading.Event()
        self.mesh_network = FMeshNetwork(self)

        self.main_log.put("[SYSTEM] FMesh Initialized")
