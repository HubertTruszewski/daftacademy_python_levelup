from sqlalchemy.orm import Session

from . import models


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
    result = db.query(models.Product.ProductID, models.Product.ProductName, models.Product.Discontinued, models.Product.SupplierID).filter(models.Shipper.ShipperID == models.Product.ProductID and models.Shipper.ShipperID == sup_id).all()
    return result
