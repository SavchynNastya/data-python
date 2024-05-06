import pytest
from scanner_handler import CheckQr


@pytest.fixture
def check_qr_instance(mocker):
    mocker.patch.object(CheckQr, 'check_in_db', return_value=True)  
    return CheckQr()


@pytest.mark.parametrize("qr_length, expected_color", [
    (3, 'Red'),
    (5, 'Green'),
    (7, 'Fuzzy Wuzzy')
])
def test_scan_valid_qr(check_qr_instance, qr_length, expected_color):
    qr = 'A' * qr_length
    check_qr_instance.check_scanned_device(qr)
    assert check_qr_instance.color == expected_color


def test_scan_invalid_qr_color(check_qr_instance):
    qr = 'A' * 4  
    check_qr_instance.check_scanned_device(qr)
    assert check_qr_instance.color is None


@pytest.mark.parametrize("qr_length", [3, 5, 7])
def test_scan_qr_not_in_db(check_qr_instance, mocker, qr_length):
    mocker.patch.object(check_qr_instance, 'send_error')  
    mocker.patch.object(check_qr_instance, 'check_in_db', return_value=None)
    qr = 'A' * qr_length
    check_qr_instance.check_scanned_device(qr)
    assert check_qr_instance.send_error.call_args[0][0] == "Not in DB"


def test_scan_valid_qr_error_handling(check_qr_instance, mocker):
    mocker.patch.object(check_qr_instance, 'send_error')  
    qr_lengths = [3, 5, 7]
    for qr_length in qr_lengths:
        qr = 'A' * qr_length
        check_qr_instance.check_scanned_device(qr)
        assert check_qr_instance.send_error.call_args is None


def test_scan_invalid_qr_error_handling(check_qr_instance, mocker):
    mocker.patch.object(check_qr_instance, 'send_error') 
    qr = 'A' * 4  
    check_qr_instance.check_scanned_device(qr)
    assert check_qr_instance.send_error.call_args[0][0] == "Error: Wrong qr length 4"


@pytest.mark.parametrize("qr_length", [3, 5, 7])
def test_scan_valid_qr_success_message(check_qr_instance, qr_length):
    qr = 'A' * qr_length
    assert check_qr_instance.can_add_device(qr) == qr
