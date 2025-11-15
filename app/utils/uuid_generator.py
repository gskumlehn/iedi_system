import uuid

def generate_uuid() -> str:
    return str(uuid.uuid4())

def generate_uuids(count: int) -> list[str]:
    return [generate_uuid() for _ in range(count)]
