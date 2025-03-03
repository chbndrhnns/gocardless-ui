import json

import pytest

from server.src.services.sync_service import (
    filter_duplicates,
    send_transactions_to_lunchmoney,
    transform_transaction,
)


@pytest.fixture
def anyio_backend():
    return "asyncio"


transactions = []


@pytest.mark.anyio
async def test_send():
    t = filter_duplicates({"booked": transactions}, "booked")
    t = transform_transaction(t[0], 141461)
    await send_transactions_to_lunchmoney([t])
