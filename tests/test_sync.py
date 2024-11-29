import pytest

from server.services.sync_service import sync_transactions, get_token_storage


# @pytest.mark.skip
def test_():
    account_id = "ac39208d-b0ad-4fde-9374-e099de0ff38a"
    sync_transactions(get_token_storage(), account_id=account_id)
