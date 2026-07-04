from typing import Any


def ensure_string(value: Any) -> str:
    if value is None:
        return ""
    return str(value)


def ensure_string_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [ensure_string(item) for item in value if ensure_string(item)]
    if isinstance(value, str) and value.strip():
        return [value.strip()]
    return []


def ensure_object_list(value: Any) -> list[dict[str, Any]]:
    if isinstance(value, list):
        return [item for item in value if isinstance(item, dict)]
    return []
