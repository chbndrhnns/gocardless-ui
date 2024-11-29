from server.services.auth import get_access_token
from server.services.sync_service import get_gocardless_transactions


def test_get_dkb():
    account_id = "b18554fe-75c7-4127-954e-0f59f465c24c"
    actual, _ = get_gocardless_transactions(
        account_id, get_access_token(), from_date="2024-11-22", to_date="2024-11-22"
    )
    assert actual == {
        "booked": [
            {
                "bankTransactionCode": "PMNT-ICDT-STDO",
                "bookingDate": "2024-11-22",
                "creditorAccount": {"iban": "DE91120300000017859299"},
                "creditorName": "Johannes Rueschel",
                "debtorAccount": {"iban": "DE70200411550132069600"},
                "debtorName": "Johannes Rueschel",
                "internalTransactionId": "64fb88cd44d8ddcaf6ab1a7908492135",
                "proprietaryBankTransactionCode": "NSTO+152+9249+000",
                "purposeCode": "RINP",
                "remittanceInformationUnstructured": "Transfer comdirect - dkb",
                "transactionAmount": {"amount": "700.0", "currency": "EUR"},
                "transactionId": "2024-11-22-08.08.00.514270",
                "valueDate": "2024-11-22",
            }
        ],
        "pending": [],
    }


def test_get_ing():
    account_id = "33e12209-1d5f-4b55-b072-3db812417b89"
    actual, _ = get_gocardless_transactions(
        account_id, get_access_token(), from_date="2024-11-22", to_date="2024-11-22"
    )
    assert actual == {
        "booked": [
            {
                "bookingDate": "2024-11-22",
                "creditorName": "AUDIBLE GMBH",
                "endToEndId": "541RZ71AMKXHFJRP                   ",
                "internalTransactionId": "8d15ff4f8dc878f5fea3c878f44575ea",
                "proprietaryBankTransactionCode": "Lastschrifteinzug",
                "remittanceInformationUnstructured": "mandatereference:0xjNei1bcEUn?iEBC24JpkhuZ88ATR,creditorid:DE31ZZZ00000563369,remittanceinformation:D01-6254502-7698230 "
                "Audible Gmbh "
                "541RZ71AMKXHFJRP",
                "transactionAmount": {"amount": "-0.99", "currency": "EUR"},
                "transactionId": "000012247539913",
                "valueDate": "2024-11-22",
            }
        ],
        "pending": [],
    }
