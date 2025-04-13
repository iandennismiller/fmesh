import sys
import time
import threading

from textual import events, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Input, Button


from . import FMesh


class FMeshTUI(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.radio_updated = False
        self.channels = set()

        self.fmesh = FMesh()

        self.main_loop_thread = threading.Thread(
            name="main loop",
            target=self.main_loop
        )
        self.main_loop_thread.start()

    def compose(self) -> ComposeResult:
        "Assemble the UI from widgets and panels"
        from .tui_widgets import main_window
        yield Header()
        yield main_window
        yield Footer()

    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        pass

    def on_input_submitted(self, event: Input.Submitted) -> None:
        source = str(event.input.id).lower()

        if source == "msg":
            self.send()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button events."""
        action = str(event.button.id).lower()

        if action == "exit":
            self.fmesh.messages.put("[SYSTEM] Exit button pressed")
            self.fmesh.halt.set()
            self.main_loop_thread.join()
            sys.exit(1)

        elif action == "send":
            self.send()

    def send(self):
        "Sending a message to the device"

        try:
            channel, message_content = self.query_one("#input-field").value.split('#')
            channel = int(channel)
        except:
            channel = 0
            message_content = self.query_one("#input-field").value

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

        self.query_one("#send").disabled = False
        self.query_one("#input-field").value = f"0#"
        self.query_one("#radio_lora").update(f"LoRa:  {lora}")
        self.query_one("#radio_longname").update(f"Name:  {long_name}")
        self.query_one("#radio_shortname").update(f"Short: {short_name}")

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

    def wait_for_ready(self):
        "wait for the app to be ready"

        ready = False
        while not ready:
            try:
                self.query_one("#messages")
                ready = True
            except Exception as e:
                time.sleep(0.25)

    def main_loop(self):
        """Main i/o loop for the app."""

        self.wait_for_ready()

        while not self.fmesh.halt.is_set():
            self.refresh_messages()

            if self.fmesh.mesh_network.is_connected:
                self.refresh_channels()

                if not self.radio_updated:
                    self.refresh_radio_info()
                    self.radio_updated = True

            time.sleep(0.1)
