import sqlite3

from fastapi import FastAPI, HTTPException
from fastapi.param_functions import Query
from pydantic import BaseModel

app = FastAPI()


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/suppliers/{supplier_id}")
async def single_supplier(supplier_id: int):
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        "SELECT CompanyName, Address FROM Suppliers WHERE SupplierID = :supplier_id",
        {'supplier_id': supplier_id}).fetchone()

    return data


@app.get("/employee_with_region")
async def employee_with_region():
    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute('''
        SELECT Employees.LastName, Employees.FirstName, Territories.TerritoryDescription
        FROM Employees JOIN EmployeeTerritories ON Employees.EmployeeID = EmployeeTerritories.EmployeeID
        JOIN Territories ON EmployeeTerritories.TerritoryID = Territories.TerritoryID;
     ''').fetchall()
    return [{"employee": f"{x['FirstName']} {x['LastName']}", "region": x["TerritoryDescription"]} for x in data]


class Customer(BaseModel):
    company_name: str


@app.post("/customers/add")
async def customers_add(customer: Customer):
    cursor = app.db_connection.execute(
        f"INSERT INTO Customers (CompanyName) VALUES ('{customer.company_name}')"
    )
    app.db_connection.commit()
    return {
        "CustomerID": cursor.lastrowid,
        "CompanyName": customer.company_name
    }


class Shipper(BaseModel):
    company_name: str


class Categories(BaseModel):
    categories: list


class Customers(BaseModel):
    customers: list


class Product(BaseModel):
    id: int
    name: str


class Employees(BaseModel):
    employees: list


class ProductsExtended(BaseModel):
    products_extended: list


@app.patch("/shippers/edit/{shipper_id}")
async def artists_add(shipper_id: int, shipper: Shipper):
    app.db_connection.execute(
        "UPDATE Shippers SET CompanyName = ? WHERE ShipperID = ?", (
            shipper.company_name, shipper_id)
    )
    app.db_connection.commit()

    app.db_connection.row_factory = sqlite3.Row
    data = app.db_connection.execute(
        """SELECT ShipperID AS shipper_id, CompanyName AS company_name
         FROM Shippers WHERE ShipperID = ?""",
        (shipper_id, )).fetchone()

    return data


@app.get("/orders")
async def orders():
    app.db_connection.row_factory = sqlite3.Row
    orders = app.db_connection.execute("SELECT * FROM Orders").fetchall()
    return {
        "orders_counter": len(orders),
        "orders": orders,
    }


@app.delete("/orders/delete/{order_id}")
async def order_delete(order_id: int):
    cursor = app.db_connection.execute(
        "DELETE FROM Orders WHERE OrderID = ?", (order_id, )
    )
    app.db_connection.commit()
    return {"deleted": cursor.rowcount}


@app.get("/region_count")
async def root():
    app.db_connection.row_factory = lambda cursor, x: x[0]
    regions = app.db_connection.execute(
        "SELECT RegionDescription FROM Regions ORDER BY RegionDescription DESC").fetchall()
    count = app.db_connection.execute('SELECT COUNT(*) FROM Regions').fetchone()

    return {
        "regions": regions,
        "regions_counter": count
    }


@app.get("/categories")
async def categories():
    categories = app.db_connection.execute(
        "SELECT CategoryID, CategoryName from Categories ORDER BY CategoryID"
    ).fetchall()
    results_list = list()
    for result in categories:
        results_list.append({"id": result[0], "name": result[1]})
    return Categories(categories=results_list)


@app.get("/customers")
async def customers():
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")
    categories = app.db_connection.execute(
        'SELECT CustomerID, ContactName, Address, PostalCode, City, Country from Customers WHERE CustomerID="VALON" ORDER BY CustomerID;'
    ).fetchall()
    results_list = list()
    for result in categories:
        full_address = str()
        full_address += result[2] if result[2] is not None else ' '
        full_address += ' '
        full_address += result[3] if result[3] is not None else ' '
        full_address += ' '
        full_address += result[4] if result[4] is not None else ' '
        full_address += ' '
        full_address += result[5] if result[5] is not None else ' '
        if len(full_address.split()) == 0:
            full_address = True
        results_list.append({"id": result[0], "name": result[1], "full_address": full_address})
    return Customers(customers=results_list)


@app.get("/products/{id}")
async def products(id: int):
    result = app.db_connection.execute(
        "SELECT ProductID, ProductName FROM Products WHERE ProductID=?", (id,)
    ).fetchone()
    if result is not None:
        return Product(id=result[0], name=result[1])
    else:
        raise HTTPException(status_code=404, detail="Not found")


@app.get("/employees")
async def employees(limit: int = Query(None), offset: int = Query(None), order: str = Query(None)):
    if order is not None and order not in {'first_name', 'last_name', 'city'}:
        raise HTTPException(status_code=400)
    order_dict = {'first_name': "FirstName", 'last_name': "LastName", 'city': "City"}
    result_list = []
    query = "SELECT EmployeeID, FirstName, LastName, City FROM Employees"
    if order is not None:
        query += f' ORDER BY {order_dict[order]}'
    if limit is not None:
        query += f' LIMIT {limit}'
    if offset is not None:
        query += f' OFFSET {offset}'
    results = app.db_connection.execute(query).fetchall()
    for result in results:
        result_list.append({'id': result[0], 'first_name': result[1], 'last_name': result[2], 'city': result[3]})
    return Employees(employees=result_list)


@app.get("/products_extended")
async def products_extended():
    results = app.db_connection.execute(
        "SELECT Products.ProductID, Products.ProductName, Categories.CategoryName, Suppliers.CompanyName "
        "FROM Products JOIN Categories ON Products.CategoryID = Categories.CategoryID "
        "JOIN Suppliers ON Products.SupplierID = Suppliers.SupplierID"
    )
    results_list = []
    for result in results:
        results_list.append({'id': result[0], 'name': result[1], 'category': result[2], 'supplier': result[3]})
    return ProductsExtended(products_extended=results_list)
