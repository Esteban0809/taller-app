from fastapi import HTTPException
from sqlalchemy.orm import Session


def no_encontrado(detalle: str):
    return HTTPException(status_code=404, detail=detalle)


def conflicto(detalle: str):
    return HTTPException(status_code=409, detail=detalle)


def guardar(db: Session, objeto=None):
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise

    if objeto is not None:
        db.refresh(objeto)

    return objeto
