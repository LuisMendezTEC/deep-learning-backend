import re
from typing import Any

SNAKE_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")
CAMEL_BOUNDARY_PATTERN = re.compile(r"(?<!^)(?=[A-Z])")


def to_snake_case(field_name: str) -> str:
    return CAMEL_BOUNDARY_PATTERN.sub("_", field_name).replace("-", "_").lower()


def find_non_snake_case_fields(payload: Any, path: str = "") -> list[dict[str, str]]:
    violations: list[dict[str, str]] = []

    if isinstance(payload, dict):
        for key, value in payload.items():
            current_path = f"{path}.{key}" if path else str(key)
            if isinstance(key, str) and not SNAKE_CASE_PATTERN.fullmatch(key):
                violations.append(
                    {
                        "field": current_path,
                        "suggested_field": to_snake_case(key),
                    }
                )
            violations.extend(find_non_snake_case_fields(value, current_path))
    elif isinstance(payload, list):
        for index, item in enumerate(payload):
            violations.extend(find_non_snake_case_fields(item, f"{path}[{index}]"))

    return violations
