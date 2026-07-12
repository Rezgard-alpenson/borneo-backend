from typing import Any, Optional


def ok(data: Any = None, message: str = "Success", meta: Optional[dict] = None) -> dict:
    result = {"success": True, "message": message, "data": data}
    if meta is not None:
        result["meta"] = meta
    return result
