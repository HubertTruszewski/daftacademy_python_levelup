from fastapi.exceptions import HTTPException
from sqlalchemy.orm import Session

from . import models, models2


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_all_suppliers(db: Session):
    return db.query(models.Supplier).with_entities(models.Supplier.SupplierID, models.Supplier.CompanyName).order_by(models.Supplier.SupplierID).all()


def get_one_supplier(db: Session, sup_id: int):
    return db.query(models.Supplier).filter(models.Supplier.SupplierID == sup_id).first()


def get_supplier_products(db: Session, sup_id: int):
    # return db.query(models2.Product).join(models2.Category).filter(models2.Product.SupplierID == sup_id).order_by(models2.Product.ProductID.desc()).all()
    return db.query(models2.Product.ProductID, models2.Product.ProductName, models2.Product.Discontinued, models2.Category).filter(models2.Product.CategoryID == models2.Category.CategoryID).filter(models2.Product.SupplierID == sup_id).order_by(models2.Product.ProductID.desc()).all()


def create_new_supplier(db: Session, supplier):
    id = db.query(models2.Supplier).count()+1
    db.add(models2.Supplier(**supplier, SupplierID=id))
    db.commit()
    return db.query(models2.Supplier).order_by(models2.Supplier.SupplierID.desc()).limit(1).first()


def modify_supplier(id: int, db: Session, suppliers):
    if db.query(models2.Supplier).filter(models2.Supplier.SupplierID == id).first() is None:
        raise HTTPException(status_code=404)
    if len(suppliers) != 0:
        db.query(models2.Supplier).filter(models2.Supplier.SupplierID == id).update(suppliers)
        db.commit()
    return db.query(models2.Supplier).filter(models2.Supplier.SupplierID == id).first()


def delete_supplier(id: int, db: Session):
    record = db.query(models2.Supplier).filter(models2.Supplier.SupplierID == id).first()
    if record is None:
        raise HTTPException(status_code=404)
    db.delete(record)
    db.commit()
