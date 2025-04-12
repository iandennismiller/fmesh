import os
import sys
import json
import time
import threading

from queue import Queue

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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fmesh = FMesh()

        self.connected = False
        self.connection_status = False
        self.radio_updated = False
        self.channels = set()

        self.main_loop_thread = threading.Thread(
            name="main loop",
            target=self.main_loop
        )
        self.main_loop_thread.start()

    def compose(self) -> ComposeResult:
        "Assemble the UI from widgets and panels"
        from .tui_widgets import ui_panel, main_log

        yield Header()
        yield ui_panel
        yield Label("", id="separator")
        yield main_log
        yield Footer()

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
            self.fmesh.main_log.put("[SYSTEM] Exit button pressed")
            self.fmesh.halt.set()
            sys.exit(1)

        elif action == "connect":
            self.connect_to_device()

        elif action == "send":
            self.send()

    def send(self):
        "Sending a message to the device"

        channel, message_content = self.query_one("#input-field").value.split('#')

        try:
            channel = int(channel)
        except:
            channel = 0

        self.fmesh.mesh_network.send_raw(message_content, channel)

        self.query_one("#input-field").value = f"{channel}#"
        self.query_one("#main_log").write(f"[MESSAGE] #{channel} {message_content}")
        self.query_one("#received_messages").write(f"[You] #{channel} > {message_content}")
    
    def connect_to_device(self):
        connect_button = self.query_one("#connect")
        connect_button.disabled = True
        
        device = self.query_one("#device").value
        if not device:
            self.fmesh.main_log.put(f"[ERROR] Radio device not set...")
            return

        self.fmesh.main_log.put(f"[RADIO] connect to device {device}")
        self.connect_thread = threading.Thread(
            name="connect",
            target=self.fmesh.mesh_network.connect,
            args=(device,),
        )
        self.connect_thread.start()

    def change_value(self, id, replacement):
        self.query_one(id).update(replacement)
    
    def refresh_main_log(self):
        "Populating the main log"

        while not self.fmesh.main_log.empty():
            msg = self.fmesh.main_log.get()
            try:
                self.query_one("#main_log").write(msg)
            except Exception as e:
                pass

    def refresh_radio_info(self):
        "Populating the radio info"
        if not self.radio_updated:
            name = self.fmesh.mesh_network.interface.getShortName()

            self.query_one("#radio_name").update(f"Connected to: {name}")
            self.query_one("#send").disabled = False

            self.query_one("#radio_namebox").update(f"Radio NAME: {name}")

            self.query_one("#radio_id").update(
                f"Radio ID (long name): {str(self.fmesh.mesh_network.interface.getLongName())}"
            )

            self.query_one("#radio_user").update(
                f"Radio USER: {str(self.fmesh.mesh_network.interface.getMyUser())}"
            )

            self.query_one("#input-field").value = f"0#"

            self.radio_updated = True

    def refresh_channels(self):
        "Populating the channels table"
        chantable = self.query_one("#channels_table")
        for chan_id in range(8):
            chan_name = self.fmesh.mesh_network.get_channel_name(chan_id)
            if chan_name and chan_id not in self.channels:
                self.channels.add(chan_id)
                chantable.add_row(str(chan_id), chan_name)

    def refresh_messages(self):
        "Populating the received messages"

        while not self.fmesh.messages_log.empty():
            msg = self.fmesh.messages_log.get()

            if msg["portnum"] == "TEXT_MESSAGE_APP":
                msg["sender"] = hex(msg["from"])[2:]

                msg["recipient"] = hex(msg["to"])[2:]
                if msg["recipient"] == "ffffffff":
                    msg["recipient"] = ""

                msg_fmt = "[!{sender}{recipient}] #{channel}:{channel_name} > {text}"
                self.query_one("#received_messages").write(msg_fmt.format(**msg))

    def main_loop(self):
        """Main i/o loop for the app."""

        # wait for the app to be ready
        ready = False
        while not ready:
            try:
                self.query_one("#main_log")
                ready = True
            except Exception as e:
                time.sleep(1)

        self.query_one("#device").value = self.fmesh.config["FMESH_DEVICE"]
        self.query_one("#connect").disabled = False

        while not self.fmesh.halt.is_set():
            self.refresh_main_log()
            if self.fmesh.mesh_network.is_connected:
                self.refresh_messages()
                self.refresh_channels()
                self.refresh_radio_info()
            time.sleep(0.1)
