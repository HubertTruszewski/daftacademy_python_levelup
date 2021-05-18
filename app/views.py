from pydantic.main import BaseModel
from app import models2
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import get_db

router = APIRouter()


class SupplierModel(BaseModel):
    CompanyName: str
    ContactName: Optional[str]
    ContactTitle: Optional[str]
    Address: Optional[str]
    City: Optional[str]
    PostalCode: Optional[str]
    Country: Optional[str]
    Phone: Optional[str]


@router.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@router.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(get_db)):
    return crud.get_shippers(db)


@router.get('/suppliers')
async def get_suppliers(db: Session = Depends(get_db)):
    return crud.get_all_suppliers(db)


@router.get('/suppliers/{id}')
async def get_suppliers_by_id(id: int, db: Session = Depends(get_db)):
    result = crud.get_one_supplier(db, id)
    if result is None:
        raise HTTPException(status_code=404)
    return result


@router.get('/suppliers/{id}/products')
async def get_supplier_products(id: int, db: Session = Depends(get_db)):
    result = crud.get_supplier_products(db, id)
    if result is None:
        raise HTTPException(status_code=404)
    return result


@router.post('/suppliers', status_code=201)
async def new_supplier(supplier: dict, db: Session = Depends(get_db)):
    return crud.create_new_supplier(db, supplier)
