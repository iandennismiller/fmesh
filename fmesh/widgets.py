from textual import events, on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.widgets import Header, Footer
from textual.widgets import Input, Label, Pretty, DataTable
from textual.widgets import Button, Static, RichLog, Sparkline, Checkbox
from textual.containers import Container, Horizontal, VerticalScroll, Vertical
from textual.validation import Function, Number, ValidationResult, Validator

CSS = """
Screen {
    layout: vertical;
}

#input-ui {
    height: 3;
}

#input-field {
    width: 1fr;
}

#send {
    height: 3;
    width: 8;
    min-width: 8;
    border: none;
}

#channels-table-container {
    width: 17;
}
"""

def get_main_window(fmesh_tui) -> Container:
    channels_table = DataTable(
        id="channels-table",
        cursor_type="row"
    )
    channels_table.add_column("#")
    channels_table.add_column("Channel name")

    ###
    # main window

    main_window = Container(
        RichLog(
            id="messages",
            auto_scroll=True
        ),
        Horizontal(
            Container(
                channels_table,
                id="channels-table-container"
            ),
            InputEnter(
                id="input-field",
                restrict=r"^$|[0-9]|[0-9]#.*",
                select_on_focus=False,
                fmesh_tui=fmesh_tui,
            ),
            Button(
                "Send",
                id="send",
                disabled=True
            ),
            id="input-ui",
        )
    )

    return main_window

class InputEnter(Input):
    BINDINGS = [
        Binding("escape", "blur"),
        Binding("enter", "enter"),
    ]

    def __init__(self, fmesh_tui, **kwargs) -> None:
        super().__init__(**kwargs)
        self.fmesh_tui = fmesh_tui

    def action_blur(self) -> None:
        """Blur (un-focus) the widget.

        Focus will be moved to the next available widget in the focus chain.
        """
        self.blur()

    def action_enter(self) -> None:
        """
        Send the message to the device.
        This could also be handled with App.on_input_submitted() if we want
        """
        self.fmesh_tui.send_message()
