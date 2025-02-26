# GoCardless CLI Manager

A command-line interface application for managing GoCardless bank account data connections. This application provides a text-based user interface to view and manage requisitions and their associated accounts.

## Architecture

The application follows a hexagonal (ports and adapters) architecture:

- **Domain Layer** (`cli/domain/`)
  - `models.py`: Core business entities (Requisition, Account)
  - `ports.py`: Interface definitions for external services
  - `services.py`: Business logic and use cases

- **Infrastructure Layer** (`cli/infrastructure/`)
  - `gocardless.py`: GoCardless API client and adapter implementation

- **UI Layer** (`cli/ui/`)
  - `screens/`: Textual UI screens and components
  - `styles.py`: Shared UI styles

## Features

- Display requisitions sorted by creation date (oldest first)
- Color-coded status indicators:
  - Red: Expired requisitions (>90 days old)
  - Yellow: Soon to expire requisitions (<14 days until expiry)
  - Green: Active requisitions
- Detailed account information view
- Real-time data refresh
- Keyboard navigation

## Installation

1. Make sure you have Python 3.7+ installed
2. Install the required dependencies:
```bash
cd cli
pip install -r requirements.txt
```

3. Set up your GoCardless API credentials in a `.env` file:
```bash
GOCARDLESS_SECRET_ID=your_secret_id
GOCARDLESS_SECRET_KEY=your_secret_key
```

## Usage

To start the application, run from the project root directory:
```bash
# First, install dependencies
pip install -r cli/requirements.txt

# Then run the application
python -m cli.main
```

### Keyboard Shortcuts

- `↑`/`↓`: Navigate through requisitions
- `Enter`: View selected requisition details
- `d`: Delete selected requisition
- `r`: Refresh data
- `q`: Quit application
- `Esc`: Return to main screen (when viewing details)

### Deleting Requisitions

To delete a requisition:
1. Select the requisition using arrow keys
2. Press `d` to initiate deletion
3. Confirm deletion in the dialog that appears
   - Click "Yes, delete" or press Enter to confirm
   - Click "Cancel" or press Escape to abort
4. The table will refresh automatically after successful deletion

### Display Information

The main screen shows a table with the following columns:
- ID: Requisition identifier
- Institution: Associated institution ID
- Status: Current status
- Created: Creation date and time
- Days until expiry: Number of days until the 90-day expiry
- Accounts: Number of associated accounts

## Error Handling

The application handles various error conditions:
- Network connectivity issues
- API authentication errors
- Invalid data responses

Errors are displayed in red and won't prevent the application from functioning with other valid data.
