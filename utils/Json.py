def size(json_dump: str) -> float:
    """
    size in KB
    """
    return len(json_dump.encode('utf-8'))/1024
