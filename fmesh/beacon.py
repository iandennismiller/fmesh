class FMeshBeacon:
    def __init__(self, fmesh):
        self.fmesh = fmesh

        self.beacon_on = False
        # Is set to false on GUI mode so that we can control the beaconing
        self.beaconing_priority_settings = True

        self.bnum = 0

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

