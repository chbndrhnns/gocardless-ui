from textual.screen import ModalScreen
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Button, Label
from textual.message import Message

from ...domain.services import RequisitionService


class DeleteConfirmationScreen(ModalScreen):
    """Screen with a dialog to confirm requisition deletion."""

    def __init__(self, requisition_id: str, service: RequisitionService):
        super().__init__()
        self.requisition_id = requisition_id
        self.service = service

    def compose(self) -> None:
        yield Container(
            Vertical(
                Label(
                    f"Are you sure you want to delete requisition {self.requisition_id}?"
                ),
                Horizontal(
                    Button("Yes, delete", variant="error", id="confirm"),
                    Button("Cancel", variant="primary", id="cancel"),
                    classes="buttons",
                ),
                classes="dialog",
            )
        )

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "confirm":
            try:
                await self.service.delete_requisition(self.requisition_id)
                self.app.push_message(self.Deleted(self.requisition_id))
            except Exception as e:
                self.app.push_message(self.Error(str(e)))
        self.app.pop_screen()

    class Deleted(Message):
        """Message sent when a requisition is deleted."""

        def __init__(self, requisition_id: str):
            super().__init__()
            self.requisition_id = requisition_id

    class Error(Message):
        """Message sent when deletion fails."""

        def __init__(self, error: str):
            super().__init__()
            self.error = error
