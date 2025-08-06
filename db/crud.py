from sqlalchemy.orm import Session
from . import models

def get_user(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def create_user(db: Session, email: str, name: str):
    db_user = models.User(email=email, name=name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_emission_record(db: Session, user_id: int, category: str, quantity: float, emission: float, scope: str):
    record = models.EmissionRecord(
        user_id=user_id,
        category=category,
        quantity=quantity,
        emission=emission,
        scope=scope
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record

def get_user_emissions(db: Session, user_id: int):
    return db.query(models.EmissionRecord).filter(models.EmissionRecord.user_id == user_id).all()
