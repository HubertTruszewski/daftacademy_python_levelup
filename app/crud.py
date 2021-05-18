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
    results = db.query(models2.Product.ProductID, models2.Product.ProductName, models2.Product.Discontinued).filter(models2.Supplier.SupplierID == sup_id).all()
    return results


def create_new_supplier(db: Session, supplier):
    db.merge(models2.Supplier(**supplier))
    db.commit()
    return db.query(models2.Supplier).order_by(models2.Supplier.SupplierID.desc()).limit(1).first()
