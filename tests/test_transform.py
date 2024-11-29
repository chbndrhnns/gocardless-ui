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
        "amount": "-700.00",
        "currency": "eur",
        "date": "2024-11-26",
        "external_id": "9799dd15f2a208fe09d1c8045c9805e5",
        "notes": "Lebensgeld fuer Isa",
        "payee": "ISA RUESCHEL",
        "status": "uncleared",
    }


def test_ing():
    tx = {
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
    actual = transform_transaction(tx, 12345)

    assert actual == {
        "account_id": 12345,
        "amount": "-0.99",
        "currency": "eur",
        "date": "2024-11-22",
        "external_id": "8d15ff4f8dc878f5fea3c878f44575ea",
        "notes": "D01-6254502-7698230 Audible Gmbh 541RZ71AMKXHFJRP",
        "payee": "AUDIBLE GMBH",
        "status": "uncleared",
    }
