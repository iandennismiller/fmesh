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

connection_info = VerticalScroll(
    Vertical(
        Label("LoRa:", id="radio_lora"),
        Label("Name:", id="radio_longname"),
        Label(
            "Short:",
            id="radio_shortname"
        ),
    ),
)

input_field = Input(
    id="input-field",
    restrict=r"^$|[0-9]|[0-9]#.*"
)
input_field.styles.width = "90%"

send_message = Horizontal(
    input_field,
    Button(
        "Send",
        id="send",
        disabled=True
    ),
)
send_message.styles.height = 4

messages = RichLog(
    id="messages",
    auto_scroll=True
)
# messages.styles.height = "70%"

about = Horizontal(
    VerticalScroll(channels_table),
    connection_info,
    Button(
        "Exit",
        id="exit"
    ),
)
about.styles.height = 4

main_window = Vertical(
    about,
    messages,
    Label(""),
    send_message,
)
