#!/usr/bin/env python3
import os
import json
import time
import threading

from textual import events, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.widgets import Input, Label, Pretty, DataTable
from textual.widgets import Button, Static, RichLog, Sparkline, Checkbox
from textual.containers import Horizontal, VerticalScroll
from textual.validation import Function, Number, ValidationResult, Validator

from dotenv import load_dotenv

from . import FMesh


class FMeshTUI(App):
    # CSS_PATH = "meshterm.tcss"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.stop_watchdog = False
        self.term_connected = False
        self.message_to_show = None

        self.fmesh = FMesh()

    # INFO Composing the app
    def compose(self) -> ComposeResult:
        """Create child widgets for the app."""
        yield Header()
        yield Footer()
        # Inputs

        dataTable = DataTable(id="channels_table", cursor_type="row")
        dataTable.add_column("#")
        dataTable.add_column("Channel name")
        

        messages = VerticalScroll(
                Label("Unknown Radio Name", id="radio_name"),
                Horizontal(
                    Input(
                        id="input-field", # or msg?
                        placeholder="Send something...",
                        restrict=r"^$|[0-9]|[0-9]#.*"),
                        Button(
                            "Send",
                            id="send",
                            disabled=True
                        ),
                    ),

                VerticalScroll(
                    #Sparkline([1, 2, 3, 3, 3, 3, 3], summary_function=min,),
                    Label("Received messages:"),
                    RichLog(id="received_messages", auto_scroll=True),
                    classes="messages-panel"
                    ),
                classes="right-top-panel")

        yield Horizontal(
            VerticalScroll(
                VerticalScroll(
                    Label("Enter the serial port to connect to: "),
                    Input(placeholder="/dev/ttyUSB0", id="port"),
                    Horizontal(
                        Button("Connect to radio", id="connect"),
                        Button("Exit", id="exit"),
                        Checkbox("Enable beaconing", False, id="beaconingBox")),
                    ),

                VerticalScroll(
                    Label(""),
                    Label("CONNECTED RADIO INFO"),
                    VerticalScroll(
                        Label("No radio connected", id="radio_namebox"),
                        Label("", id="radio_id"),
                        Label("", id="radio_user"),
                        dataTable
                        ),
                    ),
                classes="left-top-panel"
                ),

                messages

            )
                
        yield Label("", id="message_to_show")
        yield Sparkline([1, 2, 3, 3, 3, 3, 3, 3, 4, 4, 5, 5, 6, 5, 5, 4, 4, 3, 3, 3, 3, 3, 3, 3, 2, 1], summary_function=min,)
        # Main log
        yield RichLog(id="main_log", auto_scroll=True)

        # NOTE Here we start the watcher thread
        self.watchdog = threading.Thread(name="watchdog", target=self.watcher)
        self.watchdog.start()

    # SECTION Actions

    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        source = str(event.input.id).lower()
        if source == "msg":
            self.send()
        else:
            pass

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button events."""
        text_log = self.query_one("#main_log")
        action = str(event.button.id).lower()
        if action == "exit":
            try:
                self.fmesh.force_quit = True
                self.stop_watchdog = True
            except:
                print("[SYSTEM] Failed to stop thread")
            exit(1)
        elif action == "connect":
            self.connect()
        elif action == "send":
            self.send()

    # INFO Sending a message to the device
    def send(self):
        if not self.fmesh.mesh_network.connected:
            self.message_to_show = "CANNOT SEND MESSAGE: No connection"
            return

        chan, textToSend = self.query_one("#msg").value.split('#')

        try:
            chan = int(chan)
        except:
            chan = 0

        self.fmesh.mesh_network.send_raw(textToSend, chan)
        self.query_one("#msg").value = f"{chan}#"
        self.message_to_show = f"MESSAGE SENT: #{chan} " + textToSend
        self.query_one("#main_log").write(self.message_to_show)
        self.query_one("#received_messages").write(f"[You] #{chan} > " + textToSend)
    
    # INFO Managing connection to the device
    def connect(self):
        self.query_one("#connect").disabled = True
        self.query_one("#connect").value = "CONNECTING..."

        self.port = self.query_one("#port").value
        self.port = self.port.strip()

        self.message_to_show = "CONNECTING TO " + self.port + "..."

        if not self.port or self.port == "":
            self.port = None

        # start FMesh in a background thread
        # It will be controlled by this TUI
        self.instance = threading.Thread(target=self.fmesh.main)
        self.instance.start()

    def change_value(self, id, replacement):
        self.query_one(id).update(replacement)
    
    def loadEnv(self):
        self.env = {}
        with open(".env", "r") as f:
            textenv = f.readlines()
            for line in textenv:
                key, value = line.split("=")
                self.env[key.strip()] = value.strip()
        return self.env

    def saveEnv(self):
        preparedEnv = ""
        for key, value in self.env.items():
            preparedEnv += key + "=" + value + "\n"
        with open(".env", "w") as f:
            f.write(preparedEnv)
            f.flush()
        return self.env

    def watcher(self):
        while not self.stop_watchdog:
            # Refreshing the environment variables and setting ours if needed
            try:
                self.fmesh.mesh_network.beaconing_priority_settings = False
                self.fmesh.mesh_network.beacon_on = self.query_one("#beaconingBox").value
                print("[WATCHDOG] Refreshing environment variables...")
                os.environ['BEACONING'] = str(self.fmesh.mesh_network.beacon_on)
                print("[WATCHDOG] Environment variables refreshed: " + str(os.environ['BEACONING']))
            except Exception as e:
                print("[WARNING] beaconingBox element is not reachable - this may be temporary.")

            # Loading messages into the gui
            try:
                if (term.outputs != term.last_output):
                    term.last_output = term.outputs
                    self.query_one("#main_log").write(term.outputs)

                # Priority to us here
                if (self.message_to_show):
                    _message_to_show = self.message_to_show
                    self.message_to_show = None
                else:
                    _message_to_show = self.message_to_show

                self.change_value("#message_to_show", _message_to_show)

                # If we are connected we should get our variables
                if self.fmesh.mesh_network.connected:
                    if not self.term_connected:
                        name = self.fmesh.mesh_network.interface.getShortName()

                        self.query_one("#connect").disabled = False
                        self.query_one("#connect").value = "Reconnect"
                        self.query_one("#radio_name").update(f"Connected to: {name}")
                        self.query_one("#send").disabled = False

                        # Also updating our infos
                        self.query_one("#radio_namebox").update(f"Radio NAME: {name}")
                        self.query_one("#radio_id").update(
                            f"Radio ID (long name): {str(self.fmesh.mesh_network.interface.getLongName())}"
                        )
                        self.query_one("#radio_user").update(
                            f"Radio USER: {str(self.fmesh.mesh_network.interface.getMyUser())}"
                        )

                        chantable = self.query_one("#channels_table")
                        for chan_id in range(8):
                            chan_name = self.fmesh.mesh_network.get_channel_name(chan_id)
                            if chan_name != None and len(chan_name) > 0:
                                chantable.add_row(str(chan_id), chan_name)

                self.term_connected = self.fmesh.mesh_network.connected
                    
                # Populating the received messages
                for receivd in self.fmesh.mesh_network.msg_received:
                    if receivd["portnum"] == "TEXT_MESSAGE_APP":
                        #headerMessage = "[" + hex(receivd["from"]) + " -> " + hex(receivd["to"]) + "] > " 
                        sender = hex(receivd["from"])[2:]
                        to = hex(receivd["to"])[2:]
                        if to != "ffffffff":
                            to = " -> " + to
                        else:
                            to = ""
                        chan = receivd["channel"]
                        chan_name = receivd["channel_name"]
                        headerMessage = f"[!{sender}{to}] #{chan}:{chan_name} > "
                        textToShow = headerMessage + receivd["text"]
                        self.query_one("#received_messages").write(textToShow)
                        #self.query_one("#received_messages").write(repr(receivd))

                self.fmesh.mesh_network.msg_received = []

            except Exception as e:
                self.change_value("#message_to_show", "ERROR: " + str(e))

            time.sleep(1)
