def require_id(value: int | None, entity_name: str) -> int:
    if value is None:
        raise RuntimeError(f"{entity_name} must be saved before it can be referenced")
    return value
