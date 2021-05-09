import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.param_functions import Query
from pydantic import BaseModel
from starlette.responses import JSONResponse, Response
import uvicorn


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


class Orders(BaseModel):
    orders: list


class Category(BaseModel):
    id: Optional[int]
    name: str


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
    query = "SELECT CustomerID, ContactName, (COALESCE(Address, '') || ' ' || COALESCE(PostalCode, '') || ' ' || COALESCE(City, '') || ' ' || COALESCE(Country, '')) FROM Customers ORDER BY UPPER(CustomerID);"
    categories = app.db_connection.execute(query).fetchall()
    results_list = list()
    for result in categories:
        results_list.append({"id": result[0], "name": result[1], "full_address": result[2]})
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


@app.get("/products/{id}/orders")
async def products_orders(id: int):
    def calc_total_price(unit_price, quantity, discount):
        return ((unit_price * quantity) - (discount * (unit_price * quantity)))
    results = app.db_connection.execute(
        'SELECT Orders.OrderId, Customers.CompanyName, `Order Details`.quantity, `Order Details`.UnitPrice, `Order Details`.discount '
        'FROM Orders JOIN Customers ON Customers.CustomerID = Orders.CustomerID JOIN `Order Details` ON Orders.OrderID = `Order Details`.OrderID'
        ' JOIN Products ON Products.ProductID = `Order Details`.ProductID WHERE Products.ProductID = ? ORDER BY Orders.OrderID', (id, )
    ).fetchall()
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="Not found")
    results_list = []
    for result in results:
        orderid = result[0]
        companyname = result[1]
        quantity = result[2]
        unitprice = result[3]
        discount = result[4]
        total_price = calc_total_price(unitprice, quantity, discount)
        total_price = round(total_price, 2)
        results_list.append({'id': orderid, 'customer': companyname, 'quantity': quantity, 'total_price': total_price})
    return Orders(orders=results_list)


@app.post("/categories")
async def add_category(category: Category, response: Response):
    cursor = app.db_connection.cursor()
    cursor.execute(
        'INSERT INTO Categories (CategoryName) VALUES (?)', (category.name, )
    )
    app.db_connection.commit()
    new_id = cursor.lastrowid
    response.status_code = 201
    return Category(id=new_id, name=category.name)


@app.put("/categories/{id}")
async def modify_category(id: int, category: Category):
    results = app.db_connection.execute('SELECT * FROM Categories WHERE CategoryID=?', (id, )).fetchall()
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No such category")
    app.db_connection.execute(
        'UPDATE Categories SET CategoryName=:name WHERE CategoryID=:id', {"name": category.name, 'id': id}
    )
    app.db_connection.commit()
    results = app.db_connection.execute('SELECT * FROM Categories WHERE CategoryID=?', (id, )).fetchone()
    return Category(id=results[0], name=results[1])


@app.delete("/categories/{id}")
async def delete_category(id: int):
    results = app.db_connection.execute('SELECT * FROM Categories WHERE CategoryID=?', (id, )).fetchall()
    if len(results) == 0:
        raise HTTPException(status_code=404, detail="No such category")
    app.db_connection.execute(
        'PRAGMA foreign_keys=off;'
    )
    app.db_connection.execute(
        'DELETE FROM Categories WHERE CategoryID=:id', {'id': id}
    )
    app.db_connection.commit()
    msg = {"deleted": 1}
    return JSONResponse(status_code=200, content=msg)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
