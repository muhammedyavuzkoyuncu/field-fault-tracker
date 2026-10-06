from backend.app.services.fault_service import (
    normalize_fault_title,
    validate_fault_priority,
    validate_fault_status,
)


def test_valid_fault_priority():
    assert validate_fault_priority("YUKSEK") is True


def test_invalid_fault_priority():
    assert validate_fault_priority("INVALID") is False


def test_valid_fault_status():
    assert validate_fault_status("DEVAM_EDIYOR") is True


def test_invalid_fault_status():
    assert validate_fault_status("INVALID") is False


def test_normalize_fault_title():
    title = "  Motor arızası  "

    result = normalize_fault_title(title)

    assert result == "Motor arızası"