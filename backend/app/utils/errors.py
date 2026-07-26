from fastapi import HTTPException


def not_found(entity: str, entity_id: int) -> HTTPException:
    return HTTPException(status_code=404, detail=f"{entity}({entity_id}) not found")


def conflict(detail: str) -> HTTPException:
    return HTTPException(status_code=409, detail=detail)
