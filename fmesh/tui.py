import sys
import time
import threading

from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer, Input, Button
from textual.css.query import NoMatches

from . import FMesh
from .widgets import get_main_window, CSS as TUI_CSS


class FMeshTUI(App):
    CSS = TUI_CSS

    BINDINGS = [
        Binding("escape", "shutdown"),
    ]

    def action_shutdown(self) -> None:
        self.shutdown()

    def __init__(self, *args, **kwargs):
        super().__init__(ansi_color=True, *args, **kwargs)

        self.connected = False
        self.channels = set()

        self.fmesh = FMesh()

        self.main_loop_thread = threading.Thread(
            name="main loop",
            target=self.main_loop
        )
        self.main_loop_thread.start()

    def compose(self) -> ComposeResult:
        "Assemble the UI from widgets and panels"
        
        yield Header()
        yield Footer()
        yield get_main_window(self)

    def shutdown(self) -> None:
        self.fmesh.halt.set()
        self.main_loop_thread.join()
        self.exit()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button events."""
        
        action = str(event.button.id).lower()

        if action == "send":
            self.send_message()

    def send_message(self):
        "Sending a message to the device"

        try:
            channel, message_content = self.query_one("#input-field").value.split('#')
            channel = int(channel)
        except:
            channel = 0
            message_content = self.query_one("#input-field").value

        if not message_content:
            return

        self.fmesh.mesh_network.send_text(message_content, channel)

        channel_name = self.fmesh.mesh_network.get_channel_name(channel)
        msg = f"/{channel}/{channel_name}/You     : {message_content}"
        self.query_one("#messages").write(msg)

        self.query_one("#input-field").value = f"{channel}#"
    
    def refresh_radio_info(self):
        "Populating the radio info"

        short_name = self.fmesh.mesh_network.interface.getShortName()
        long_name = self.fmesh.mesh_network.interface.getLongName()
        lora = self.fmesh.mesh_network.interface.getMyUser()["id"]

        self.sub_title = f"{short_name} ({lora})"

    def refresh_channels(self):
        "Populating the channels table"

        try:
            chantable = self.query_one("#channels-table")
        except NoMatches:
            return

        for chan_id in range(8):
            chan_name = self.fmesh.mesh_network.get_channel_name(chan_id)

            if chan_name and chan_id not in self.channels:
                self.channels.add(chan_id)
                chantable.add_row(str(chan_id), chan_name)

    def refresh_messages(self):
        "Populating the received messages"

        while not self.fmesh.messages.empty():
            msg = self.fmesh.messages.get()

            if type(msg) == str:
                self.query_one("#messages").write(msg)
            else:
                if msg["portnum"] == "TEXT_MESSAGE_APP":
                    msg["sender"] = hex(msg["from"])[2:]

                    msg["recipient"] = hex(msg["to"])[2:]
                    if msg["recipient"] == "ffffffff":
                        msg["recipient"] = ""

                    msg_fmt = "/{channel}/{channel_name}/{sender}: {text}"
                    self.query_one("#messages").write(msg_fmt.format(**msg))

    def wait_for_textual(self, wait=1):
        "wait for the app to be ready"

        ready = False
        start_time = time.time()
        while not ready:
            try:
                self.query_one("#messages")
                return True
            except Exception as e:
                if time.time() - start_time > wait:
                    return False
                time.sleep(0.25)

    def wait_for_device(self, wait=2):
        start_time = time.time()
        while not self.fmesh.mesh_network.connected:
            if time.time() - start_time > wait:
                return False
            time.sleep(0.1)
        return True

    def on_connect(self):
        # ensures this runs only once when the radio is connected
        self.refresh_radio_info()

        # focus on the input field and set default channel
        channel = self.fmesh.config.get("FMESH_CHANNEL", 0)
        self.query_one("#input-field").value = f"{channel}#"
        self.query_one("#input-field").focus()
        self.query_one("#send").disabled = False

        self.connected = True

    def main_loop(self):
        """Main i/o loop for the app."""

        if not self.wait_for_textual():
            self.fmesh.messages.put("[SYSTEM] Textual not ready")
            self.refresh_messages()
            return

        self.refresh_messages()
        
        if not self.wait_for_device():
            self.fmesh.messages.put("[SYSTEM] Could not initialize radio device")
            self.refresh_messages()
            return

        while not self.fmesh.halt.is_set():
            self.refresh_messages()

            if self.fmesh.mesh_network.connected:
                self.refresh_channels()

                # if the radio info has not been updated yet
                if not self.connected:
                    self.on_connect()

            time.sleep(0.1)
