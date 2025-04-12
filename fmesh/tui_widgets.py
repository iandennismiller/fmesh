from textual import events, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.widgets import Input, Label, Pretty, DataTable
from textual.widgets import Button, Static, RichLog, Sparkline, Checkbox
from textual.containers import Horizontal, VerticalScroll, Vertical
from textual.validation import Function, Number, ValidationResult, Validator


channels_table = DataTable(
    id="channels_table",
    cursor_type="row"
)
channels_table.add_column("#")
channels_table.add_column("Channel name")

received_messages = VerticalScroll(
    #Sparkline([1, 2, 3, 3, 3, 3, 3], summary_function=min,),
    Label("Received messages:"),
    RichLog(
        id="received_messages",
        auto_scroll=True,
    ),
    classes="messages-panel"
)

send_message = Vertical(
    Input(
        id="input-field",
        placeholder="Send something...",
        restrict=r"^$|[0-9]|[0-9]#.*"
    ),
    Button(
        "Send",
        id="send",
        disabled=True
    ),
)

connect_device = VerticalScroll(
    Label("Enter the serial device to connect to: "),
    Input(
        id="device",
        value="/dev/ttyUSB0",
    ),
    Horizontal(
        Button(
            "Connect to radio",
            id="connect",
            disabled=True,
        ),
        Button(
            "Exit",
            id="exit"
        ),
        # Checkbox("Enable beaconing", False, id="beaconingBox")
    ),
)

connection_info = VerticalScroll(
    Label(""),
    Label("CONNECTED RADIO INFO"),
    VerticalScroll(
        Label(
            "No radio connected",
            id="radio_namebox"
        ),
        Label("", id="radio_id"),
        Label("", id="radio_user"),
        channels_table
    ),
)

main_log = RichLog(
    id="main_log",
    auto_scroll=True
)
main_log.styles.height = 6

###
# Panels

connection_panel = Vertical(
    connect_device,
    connection_info,
    classes="left-top-panel"
)

communication_panel = Vertical(
    Label(
        "Unknown Radio Name",
        id="radio_name"
    ),
    send_message,
    received_messages,
    classes="right-top-panel"
)

ui_panel = Horizontal(
    connection_panel,
    communication_panel,
)
