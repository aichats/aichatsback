from .uuid import is_valid_uuid


def test_is_valid_uuid():
    # Valid UUIDs
    assert is_valid_uuid('7b2e01cc-fb38-4bde-9fc7-6c0ea69e2a74') is True
    assert is_valid_uuid('123e4567-e89b-12d3-a456-426614174000') is True

    # Invalid UUIDs
    assert is_valid_uuid('not-a-uuid') is False
    assert is_valid_uuid('') is False
    assert is_valid_uuid(12345) is False
    assert is_valid_uuid(None) is False
    assert is_valid_uuid('null') is False
    assert is_valid_uuid(':id') is False
