from application.users.services.study_identity import (
    format_study_identity,
    normalize_study_field,
)


def test_normalize_study_field_trims_and_limits():
    assert normalize_study_field("  ПГНИУ  ", max_len=255) == "ПГНИУ"
    assert normalize_study_field("", max_len=255) is None
    assert normalize_study_field(None, max_len=255) is None


def test_format_study_identity_joins_parts():
    assert format_study_identity("ПГНИУ", "ИВТ-41") == "ПГНИУ · ИВТ-41"
    assert format_study_identity("ПГНИУ", None) == "ПГНИУ"
    assert format_study_identity(None, None) is None
