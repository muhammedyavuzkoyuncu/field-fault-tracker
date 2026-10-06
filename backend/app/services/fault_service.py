def validate_fault_priority(priority: str) -> bool:
    allowed_priorities = {
        "DUSUK",
        "ORTA",
        "YUKSEK",
    }

    return priority in allowed_priorities


def validate_fault_status(status: str) -> bool:
    allowed_statuses = {
        "ACIK",
        "DEVAM_EDIYOR",
        "KAPALI",
    }

    return status in allowed_statuses


def normalize_fault_title(title: str) -> str:
    return title.strip()