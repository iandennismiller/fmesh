from textual import events, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.widgets import Input, Label, Pretty, DataTable
from textual.widgets import Button, Static, RichLog, Sparkline, Checkbox
from textual.containers import Horizontal, VerticalScroll, Vertical
from textual.validation import Function, Number, ValidationResult, Validator


###
# about

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

about = Horizontal(
    VerticalScroll(channels_table),
    connection_info,
    Button(
        "Exit",
        id="exit"
    ),
)
about.styles.height = 3

###
# messages

input_field = Input(
    id="input-field",
    restrict=r"^$|[0-9]|[0-9]#.*"
)
input_field.styles.width = "90%"

input_ui = Horizontal(
    input_field,
    Button(
        "Send",
        id="send",
        disabled=True
    ),
)
input_ui.styles.height = 4

messages = RichLog(
    id="messages",
    auto_scroll=True
)

###
# main window

main_window = Vertical(
    about,
    Label(""),
    messages,
    Label(""),
    input_ui,
)
