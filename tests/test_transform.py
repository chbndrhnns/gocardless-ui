import pytest

from server import transform_transaction

pytestmark = [pytest.mark.anyio]


@pytest.fixture
def anyio_backend():
    return "asyncio"


async def test_dkb():
    tx = {
        "transactionId": "2024-11-26-00.17.02.252833",
        "bookingDate": "2024-11-26",
        "valueDate": "2024-11-26",
        "transactionAmount": {"amount": "-700.0", "currency": "EUR"},
        "creditorName": "ISA",
        "debtorName": "Johannes",
        "remittanceInformationUnstructured": "Lebensgeld fuer Isa",
        "purposeCode": "RINP",
        "bankTransactionCode": "",
        "proprietaryBankTransactionCode": "",
        "internalTransactionId": "9799dd15f2a208fe09d1c8045c9805e5",
    }

    actual = await transform_transaction(tx, 12345)

    assert actual == {
        "amount": "-700.00",
        "asset_id": 12345,
        "currency": "eur",
        "date": "2024-11-26",
        "external_id": "9799dd15f2a208fe09d1c8045c9805e5",
        "notes": "Lebensgeld fuer Isa",
        "payee": "ISA",
        "status": "uncleared",
    }


async def test_ing():
    tx = {
        "bookingDate": "2024-11-22",
        "creditorName": "AUDIBLE GMBH",
        "endToEndId": "                   ",
        "internalTransactionId": "8d15ff4f8dc878f5fea3c878f44575ea",
        "proprietaryBankTransactionCode": "Lastschrifteinzug",
        "remittanceInformationUnstructured": "mandatereference:0xjNei1bcEUn?iEBC24JpkhuZ8,creditorid:DE31ZZZ00000563,remittanceinformation:D01-6254502-7698 "
        "Audible Gmbh "
        "541RZ71AMKXHF",
        "transactionAmount": {"amount": "-0.99", "currency": "EUR"},
        "transactionId": "000012247539913",
        "valueDate": "2024-11-22",
    }
    actual = await transform_transaction(tx, 12345)

    assert actual == {
        "amount": "-0.99",
        "asset_id": 12345,
        "currency": "eur",
        "date": "2024-11-22",
        "external_id": "8d15ff4f8dc878f5fea3c878f44575ea",
        "notes": "D01-6254502-7698 Audible Gmbh 541RZ71AMKXHF",
        "payee": "AUDIBLE GMBH",
        "status": "uncleared",
    }
