import uuid
from typing import Any

from config import alog


def is_valid_uuid(string: str, version=4) -> bool:
    try:
        s = str(string)
        uuid.UUID(hex=s, version=version)  # TODO: versioning isn't working
        # return s == uuid_obj.hex
        return True
    except ValueError as e:
        alog.exception(__name__, exc_info=e)
        return False
