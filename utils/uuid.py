import uuid


def is_valid_uuid(string) -> bool:
    try:
        uuid_obj = uuid.UUID(hex=str(string))
        return str(uuid_obj) == string
    except ValueError:
        return False
