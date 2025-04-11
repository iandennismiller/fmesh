import os
import time

from dotenv import load_dotenv

from fmesh.network import MeshNetwork


import builtins as __builtin__
# Overriding print for the GUI
def print(*args, **kwargs):
    global outputs
    outputs = "".join(map(str, args))
    __builtin__.print(*args, **kwargs)


class FMesh:
    def __init__(self):
        "INFO Initializing FMesh structure"
        print("[SYSTEM] Starting FMesh...")

        self.outputs = ""
        self.last_output = ""
        self.message_to_show = ""
        self.last_message_to_show = ""
        self.force_quit = False
        self.beacon_cooldown = 0

        self.vars = {}

        load_dotenv()

        # Parsing the port
        if not os.getenv('PORT') == "default":
            self.vars['port'] = os.getenv('PORT')

        print(self.vars['port'])

        self.mesh_network = MeshNetwork()
        self.mesh_network.connect(self.vars['port'])

        print("[LOADER] Initialized")

    def update_gui(self):
        # This is just a way to check if we need to notify the gui
        connection_status = self.mesh_network.connected
        if (connection_status != self.is_connected):
            print("[GUI] Changed connection status")
            self.message_to_show = "CONNECTION ESTABLISHED"
            self.is_connected = connection_status

        # NOTE Reloading .env ensures that we can control the app cycle externally
        load_dotenv()

        # NOTE Overriding is always possible, otherwise we have to rely on gui.py
        if self.mesh_network.beaconing_priority_settings:
            #print("[MAIN CYCLE] Terminal mode: getting beaconing from .env...")
            self.mesh_network.beacon_on = (os.getenv('BEACONING')=="True")
        else:
            #print("[MAIN CYCLE] GUI mode: getting beaconing from GUI...")           
            pass

        #print(f"[MAIN CYCLE] Beaconing: {self.mesh_network.beacon_on}")
        # NOTE As the scenarios can include long range radios, we have low bandwidth.
        # By waiting N seconds between beacons, we ensure that we are not beaconing
        # too often and spamming the radio channel with beacons.
        if self.mesh_network.beacon_on:
            print("[MAIN CYCLE] Checking for beacon cooldown...")

            # The following keeps the code running while we cooldown beaconing too
            if (self.beacon_cooldown > 0):
                if not self.cooldown_header:
                    print("+++ COOLDOWN ACTIVE +++")
                    self.cooldown_header = True

                if self.beacon_cooldown % 10 == 0:
                    print(f"[MAIN CYCLE] Beacon cooldown: {str(self.beacon_cooldown)}")

                self.beacon_cooldown -= 1
            else:
                print("*** COOLDOWN COMPLETE ***")
                print("[MAIN CYCLE] Beaconing is activated, proceeding...")
                self.beacon_cooldown = int(os.getenv('BEACONING_INTERVAL'))
                self.mesh_network.beacon()
                print("[MAIN CYCLE] Beacon emitted. Proceeding to the next cycle...")
        else:
            #print("[MAIN CYCLE] Beaconing is not activated, proceeding...")
            pass

    def main(self):
        "Main event loop"

        print("[EVENT LOOP] Starting watchdog...")

        self.is_connected = False
        self.cooldown_header = False

        while not ((os.getenv('FORCE_QUIT')=="True") or self.force_quit):
            self.update_gui()

            # Sleep for N seconds
            # print("[MAIN CYCLE] Sleeping for " + os.getenv('SLEEP_INTERVAL') + " seconds")
            time.sleep(int(os.getenv('SLEEP_INTERVAL')))
            # print("[MAIN CYCLE] Sleeping complete. Proceeding to the next cycle...")
