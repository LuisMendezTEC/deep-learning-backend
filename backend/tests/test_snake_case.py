from app.core.snake_case import find_non_snake_case_fields, to_snake_case


def test_to_snake_case_converts_frontend_camel_case_fields() -> None:
    assert to_snake_case("firstName") == "first_name"
    assert to_snake_case("lastName") == "last_name"
    assert to_snake_case("audioDurationSeconds") == "audio_duration_seconds"


def test_find_non_snake_case_fields_reports_nested_paths() -> None:
    payload = {
        "firstName": "Ana",
        "profile": {
            "lastName": "Soto",
        },
        "items": [
            {"createdAt": "2026-06-15"},
        ],
    }

    violations = find_non_snake_case_fields(payload)

    assert violations == [
        {"field": "firstName", "suggested_field": "first_name"},
        {"field": "profile.lastName", "suggested_field": "last_name"},
        {"field": "items[0].createdAt", "suggested_field": "created_at"},
    ]
