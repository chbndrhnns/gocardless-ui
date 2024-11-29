import pytest

from server.services.sync_service import sync_transactions, get_token_storage


@pytest.mark.skip
def test_():
    sync_transactions(
        get_token_storage(), account_id="33e12209-1d5f-4b55-b072-3db812417b89"
    )
