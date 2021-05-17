from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt
from sqlalchemy.orm import Session
from .models2 import Shipper

from . import crud, schemas
from .database import get_db

router = APIRouter()


@router.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@router.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(get_db)):
    return crud.get_shippers(db)


@router.get('/suppliers', response_model=List[Shipper])
async def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_all_suppliers(db)


@router.get('/suppliers/{id}', response_model=Shipper)
async def get_suppliers_by_id(id: int, db: Session = Depends(get_db)):
    result = crud.get_one_supplier(db, id)
    if result is None:
        raise HTTPException(status_code=404)
    return result
