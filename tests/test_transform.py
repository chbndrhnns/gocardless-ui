from server.services.sync_service import transform_transaction


def test_dkb():
    tx = {
        "transactionId": "2024-11-26-00.17.02.252833",
        "bookingDate": "2024-11-26",
        "valueDate": "2024-11-26",
        "transactionAmount": {"amount": "-700.0", "currency": "EUR"},
        "creditorName": "ISA RUESCHEL",
        "creditorAccount": {"iban": "DE92120300001036732731"},
        "debtorName": "Johannes Rüschel",
        "debtorAccount": {"iban": "DE91120300000017859299"},
        "remittanceInformationUnstructured": "Lebensgeld fuer Isa",
        "purposeCode": "RINP",
        "bankTransactionCode": "PMNT-ICDT-STDO",
        "proprietaryBankTransactionCode": "NSTO+117+7000+997",
        "internalTransactionId": "9799dd15f2a208fe09d1c8045c9805e5",
    }

    actual = transform_transaction(tx, 12345)

    assert actual == {
        "account_id": 12345,
        "amount": "700.0000",
        "currency": "eur",
        "date": "2024-11-26",
        "external_id": "2024-11-26-00.17.02.252833",
        "notes": "Lebensgeld fuer Isa",
        "payee": "Johannes Rüschel",
        "status": "uncleared",
    }
