from __future__ import annotations

import math
from numbers import Integral, Real


def _sanitize_json_value(value):
    if isinstance(value, dict):
        return {key: _sanitize_json_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_sanitize_json_value(item) for item in value]
    if isinstance(value, tuple):
        return tuple(_sanitize_json_value(item) for item in value)
    if isinstance(value, set):
        return [_sanitize_json_value(item) for item in value]
    if isinstance(value, Integral) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, Real) and not isinstance(value, bool):
        number = float(value)
        if not math.isfinite(number):
            return None
        return number
    return value


def ok(data, message: str = "success") -> dict:
    return {"code": 200, "message": message, "data": _sanitize_json_value(data)}
