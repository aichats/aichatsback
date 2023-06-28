from uuid import uuid1, uuid3, uuid4

from .uuid import is_valid_uuid


def test_is_valid_uuid():
    test_cases = [
        # Valid UUIDs
        ('7b2e01cc-fb38-4bde-9fc7-6c0ea69e2a74', True),
        ('123e4567-e89b-12d3-a456-426614174000', True),
        # Invalid UUIDs
        ('not-a-uuid', False),
        ('', False),
        (12345, False),
        (None, False),
        ('null', False),
        (':id', False),
        ('{{chat_id}}', False),
        (uuid4().hex, True),
        (uuid4().hex, True),
        (uuid4().hex + 'r', False),
        ('fbdbd35ba138483694a7434a6301fcb3', True),
    ]

    for uuid_str, expected_result in test_cases:
        assert is_valid_uuid(uuid_str) == expected_result
