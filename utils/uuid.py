import uuid

from config import alog


def is_valid_uuid(string) -> bool:
    try:
        uuid_obj = uuid.UUID(hex=str(string))
        return str(uuid_obj) == string
    except ValueError as e:
        alog.exception(__name__, e)
        return False
