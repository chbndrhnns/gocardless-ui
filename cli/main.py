"""Main entry point for the GoCardless CLI application."""

import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.append(project_root)

from cli.domain.services import RequisitionService
from cli.infrastructure.gocardless import GoCardlessAdapter
from cli.ui.screens import RequisitionsApp


def main():
    """Initialize and run the application."""
    try:
        # Initialize infrastructure
        adapter = GoCardlessAdapter()

        # Initialize domain services
        service = RequisitionService(requisition_port=adapter, account_port=adapter)

        # Initialize and run UI
        app = RequisitionsApp(service)
        app.run()

    except Exception as e:
        print(f"Failed to start application: {str(e)}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
