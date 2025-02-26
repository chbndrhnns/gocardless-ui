from textual.app import App
from textual.widgets import Header, Footer, DataTable
from textual.binding import Binding

from ...domain.services import RequisitionService
from ...domain.models import Requisition
from ..styles import STYLES
from .account_details import AccountDetailsScreen
from .delete_confirmation import DeleteConfirmationScreen


class RequisitionsApp(App):
    """Main application screen."""

    BINDINGS = [
        Binding("r", "refresh", "Refresh"),
        Binding("q", "quit", "Quit"),
        Binding("enter", "view_details", "View Details"),
        Binding("d", "delete", "Delete", show=True),
    ]

    CSS = STYLES

    def __init__(self, service: RequisitionService):
        super().__init__()
        self.service = service

    def compose(self) -> None:
        """Create and mount the widgets."""

        # Create the main table
        table = DataTable()
        table.add_columns(
            "ID", "Institution", "Status", "Created", "Days until expiry", "Accounts"
        )

        yield Header(show_clock=True)
        yield table
        yield Footer()

    async def on_mount(self) -> None:
        """Load initial data when the app is mounted."""
        await self.refresh_data()

    async def refresh_data(self) -> None:
        """Refresh the requisitions data."""
        table = self.query_one(DataTable)
        table.clear()

        try:
            # Get requisitions data
            requisitions = await self.service.get_requisitions()

            for req in requisitions:
                try:
                    row_key = table.add_row(
                        req.id,
                        req.institution_id,
                        req.status,
                        req.created.strftime("%Y-%m-%d %H:%M"),
                        f"{req.days_until_expiry} days",
                        f"{len(req.accounts)} accounts",
                    )
                    table.rows[row_key].style = req.expiry_status
                except Exception as e:
                    # If we fail to process one requisition, continue with others
                    row_key = table.add_row(
                        req.id,
                        req.institution_id,
                        "ERROR",
                        "ERROR",
                        "ERROR",
                        f"Error: {str(e)}",
                    )
                    table.rows[row_key].style = "expired"
        except Exception as e:
            table.add_column("Error")
            row_key = table.add_row(f"Failed to load requisitions: {str(e)}")
            table.rows[row_key].style = "expired"

    async def action_refresh(self) -> None:
        """Refresh the data."""
        await self.refresh_data()

    async def action_quit(self) -> None:
        """Quit the application."""
        self.exit()

    async def action_view_details(self) -> None:
        """View details of the selected requisition."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            if row and row[0] != "ERROR" and not row[0].startswith("Failed"):
                requisition = await self.service.get_requisition_details(row[0])
                await self.push_screen(AccountDetailsScreen(requisition))

    async def action_delete(self) -> None:
        """Delete the selected requisition."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            if row and row[0] != "ERROR" and not row[0].startswith("Failed"):
                await self.push_screen(DeleteConfirmationScreen(row[0], self.service))

    async def on_delete_confirmation_screen_deleted(
        self, message: DeleteConfirmationScreen.Deleted
    ) -> None:
        """Handle successful deletion."""
        await self.refresh_data()

    async def on_delete_confirmation_screen_error(
        self, message: DeleteConfirmationScreen.Error
    ) -> None:
        """Handle deletion error."""
        table = self.query_one(DataTable)
        row_key = table.add_row(f"Failed to delete requisition: {message.error}")
        table.rows[row_key].style = "expired"
