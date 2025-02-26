"""Shared styles for the UI components."""

STYLES = """
Screen {
    align: center middle;
}

DataTable {
    height: 1fr;
    margin: 1;
    border: solid $accent;
}

DataTable > .expired {
    color: red;
    text-style: bold;
}

DataTable > .expiring_soon {
    color: yellow;
    text-style: bold;
}

DataTable > .active {
    color: green;
}

#account_details {
    width: 80%;
    height: 80%;
    border: solid $accent;
    padding: 1;
}

ScrollableContainer {
    height: auto;
    border: solid $accent;
    padding: 1;
}

DataTable > .header {
    background: $accent;
    color: $text;
    text-style: bold;
}

DeleteConfirmationScreen {
    align: center middle;
}

.dialog {
    padding: 1;
    width: 60;
    height: 11;
    border: thick $accent;
    background: $surface;
}

.buttons {
    width: 100%;
    align-horizontal: center;
    margin-top: 1;
}

Button {
    margin: 1 2;
}
"""
