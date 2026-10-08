def parse_boolean(val) -> bool:
    # Bug: crashes if val is integer or boolean already
    v = val.strip().lower()
    if v in ("true", "yes", "1"):
        return True
    elif v in ("false", "no", "0"):
        return False
    raise ValueError(f"Cannot parse boolean from {val}")
