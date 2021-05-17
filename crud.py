from sqlalchemy.orm import Session
import models


def get_all_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID).all()


def get_one_supplier(db: Session, sup_id: int):
    return db.query(models.Supplier).filter(models.Supplier.SupplierID == sup_id).first()
