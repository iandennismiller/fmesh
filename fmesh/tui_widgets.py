from textual import events, on
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer
from textual.widgets import Input, Label, Pretty, DataTable
from textual.widgets import Button, Static, RichLog, Sparkline, Checkbox
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.validation import Function, Number, ValidationResult, Validator


channels_table = DataTable(
    id="channels-table",
    cursor_type="row"
)
channels_table.add_column("#")
channels_table.add_column("Channel name")

about = Horizontal(
    Container(channels_table, id="channels-table-container"),
    Button(
        "Exit",
        id="exit"
    ),
    id="about",
)

input_ui = Horizontal(
    Input(
        id="input-field",
        restrict=r"^$|[0-9]|[0-9]#.*"
    ),
    Button(
        "Send",
        id="send",
        disabled=True
    ),
    id="input-ui",
)

messages = RichLog(
    id="messages",
    auto_scroll=True
)

###
# main window

main_window = Container(
    about,
    messages,
    input_ui,
)
