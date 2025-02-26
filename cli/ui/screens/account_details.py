from textual.screen import Screen
from textual.containers import Container, ScrollableContainer
from textual.widgets import Static
from textual.binding import Binding

from ...domain.models import Requisition


class AccountDetailsScreen(Screen):
    """Screen for displaying account details."""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back", show=True),
    ]

    def __init__(self, requisition: Requisition):
        super().__init__()
        self.requisition = requisition

    def compose(self):
        yield Container(
            ScrollableContainer(
                Static(f"Requisition ID: {self.requisition.id}"),
                Static(f"Institution: {self.requisition.institution_id}"),
                Static(f"Status: {self.requisition.status}"),
                Static("\nAccounts:"),
                *[
                    Static(
                        f"\nAccount ID: {account.id}\n"
                        f"IBAN: {account.iban or 'N/A'}\n"
                        f"Currency: {account.currency or 'N/A'}\n"
                        f"Status: {account.status}"
                    )
                    for account in self.requisition.accounts
                ],
                id="account_details",
            )
        )
