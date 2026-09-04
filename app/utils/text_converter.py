
def dict_to_text(data: dict, exclude_keys=None):
    parts = []
    exclude_keys = exclude_keys or []

    for k, v in data.items():
        if k in exclude_keys:
            continue

        if v is None:
            continue

        if isinstance(v, list):
            v = "、".join(map(str, v))

        elif isinstance(v, dict):
            v = dict_to_text(v)

        parts.append(f"{k}:{v}")

    return ",".join(parts)