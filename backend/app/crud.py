from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models

def upsert_coach(db: Session, data: dict):
    ext = data.get("external_id")
    if not ext:
        raise ValueError("external_id required")

    stmt = select(models.Coach).where(models.Coach.external_id == ext)
    obj = db.scalars(stmt).first()
    if obj:
        for k,v in data.items():
            setattr(obj, k, v)
    else:
        obj = models.Coach(**data)
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj
