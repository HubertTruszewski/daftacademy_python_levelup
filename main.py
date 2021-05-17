import os
from fastapi import APIRouter, HTTPException
from fastapi.params import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
import crud
from database import get_db


DATABASE_URL = os.getenv('SQLALCHEMY_DB_URL')

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

router = APIRouter()


@router.get('/suppliers')
async def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_all_suppliers(db)


@router.get('/suppliers/{id}')
async def get_suppliers_by_id(id: int, db: Session = Depends(get_db)):
    result = crud.get_one_supplier(db, id)
    if result is None:
        raise HTTPException(status_code=404)
