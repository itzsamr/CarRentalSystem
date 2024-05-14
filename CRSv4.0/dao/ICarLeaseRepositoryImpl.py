from .ICarLeaseRepository import ICarLeaseRepository
from datetime import datetime
from entity.vehicle import Vehicle
from entity.lease import Lease
from entity.customer import Customer
from entity.payment import Payment
from typing import List
from exception.myexceptions import *
from util.DBConnection import DBConnection


class ICarLeaseRepositoryImpl(ICarLeaseRepository):
    def __init__(self):
        self.connection = DBConnection.getConnection()

    def execute_query(self, query):
        cursor = self.connection.cursor()
        cursor.execute(query)
        self.connection.commit()  # Commit changes to the database
        return cursor.fetchall()

    def _execute_and_fetch_one(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        return cursor.fetchone()

    def _execute_and_fetch_all(self, query, params=None):
        cursor = self.connection.cursor()
        cursor.execute(query, params) if params else cursor.execute(query)
        return cursor.fetchall()

    def _fetch_vehicle(self, row):
        return {
            "vehicleID": row[0],
            "make": row[1],
            "model": row[2],
            "year": row[3],
            "dailyRate": row[4],
            "status": row[5],
            "passengerCapacity": row[6],
            "engineCapacity": row[7],
        }

    def add_car(
        self,
        make: str,
        model: str,
        year: int,
        daily_rate: float,
        status: str,
        passenger_capacity: int,
        engine_capacity: float,
    ) -> None:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO Vehicle (make, model, year, dailyRate, status, passengerCapacity, engineCapacity) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        make,
                        model,
                        year,
                        daily_rate,
                        status,
                        passenger_capacity,
                        engine_capacity,
                    ),
                )
            print("Car added successfully.")
        except Exception as e:
            print(f"Error adding car: {e}")

    def remove_car(self, vehicle_id: int) -> None:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("DELETE FROM Vehicle WHERE vehicleID = ?", (vehicle_id,))
                if cursor.rowcount == 0:
                    raise VehicleNotFoundException(
                        f"Car with ID {vehicle_id} not found."
                    )
                else:
                    print("Car removed successfully.")
        except VehicleNotFoundException as cne:
            print(cne)
        except Exception as e:
            print(f"Error removing car: {e}")

    def list_available_cars(self) -> List:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM Vehicle WHERE status = 'available'")
                cars = [self._fetch_vehicle(row) for row in cursor.fetchall()]
            return cars
        except Exception as e:
            print(f"Error listing available cars: {e}")

    def list_rented_cars(self) -> List[dict]:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM Vehicle WHERE status = 'notAvailable'")
                cars = [self._fetch_vehicle(row) for row in cursor.fetchall()]
            return cars
        except Exception as e:
            print(f"Error listing rented cars: {e}")

    def find_car_by_id(self, vehicle_id: int) -> dict:
        try:
            with self.connection:
                row = self._execute_and_fetch_one(
                    "SELECT * FROM Vehicle WHERE vehicleID = ?", (vehicle_id,)
                )
            if row:
                return self._fetch_vehicle(row)
            else:
                raise VehicleNotFoundException(f"Car with ID {vehicle_id} not found.")
        except VehicleNotFoundException as cne:
            print(cne)
        except Exception as e:
            print(f"Error finding car: {e}")

    def add_customer(
        self,
        customer_id: int,
        first_name: str,
        last_name: str,
        email: str,
        phone_number: str,
    ) -> None:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO Customer (customerID, firstName, lastName, email, phoneNumber) VALUES (?, ?, ?, ?, ?)",
                    (customer_id, first_name, last_name, email, phone_number),
                )
        except Exception as e:
            print(f"Error adding customer: {e}")

    def remove_customer(self, customer_id: int) -> None:
        with self.connection:
            cursor = self.connection.cursor()
            cursor.execute(
                "DELETE FROM Payment WHERE leaseID IN (SELECT leaseID FROM Lease WHERE customerID = ?)",
                (customer_id,),
            )
            cursor.execute("DELETE FROM Lease WHERE customerID = ?", (customer_id,))
            cursor.execute("DELETE FROM Customer WHERE customerID = ?", (customer_id,))

    def list_customers(self) -> List[dict]:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM Customer")
                customers = [
                    {
                        "customerID": row[0],
                        "firstName": row[1],
                        "lastName": row[2],
                        "email": row[3],
                        "phoneNumber": row[4],
                    }
                    for row in cursor.fetchall()
                ]
            return customers
        except Exception as e:
            print(f"Error listing customers: {e}")

    def find_customer_by_id(self, customer_id: int) -> dict:
        try:
            with self.connection:
                row = self._execute_and_fetch_one(
                    "SELECT * FROM Customer WHERE customerID = ?", (customer_id,)
                )
            if row:
                return {
                    "customerID": row[0],
                    "firstName": row[1],
                    "lastName": row[2],
                    "email": row[3],
                    "phoneNumber": row[4],
                }
            else:
                raise CustomerNotFoundException(
                    f"Customer with ID {customer_id} not found."
                )
        except CustomerNotFoundException as cne:
            print(cne)
        except Exception as e:
            print(f"Error finding customer: {e}")

    def create_lease(
        self,
        customer_id: int,
        car_id: int,
        start_date: datetime,
        end_date: datetime,
        lease_type: str,
    ) -> None:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO Lease (customerID, vehicleID, startDate, endDate, type) VALUES (?, ?, ?, ?, ?)",
                    (customer_id, car_id, start_date, end_date, lease_type),
                )
            print("Lease created successfully.")
        except Exception as e:
            print(f"Error creating lease: {e}")

    def return_car(self, lease_id: int) -> None:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(
                    "UPDATE Lease SET endDate = ? WHERE leaseID = ?",
                    (datetime.now(), lease_id),
                )
                if cursor.rowcount == 0:
                    raise LeaseNotFoundException(f"Lease with ID {lease_id} not found.")
                else:
                    print("Car returned successfully.")
        except LeaseNotFoundException as lne:
            print(lne)
        except Exception as e:
            print(f"Error returning car: {e}")

    def list_active_leases(self) -> List[Lease]:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM Lease WHERE endDate IS NULL")
                leases = [
                    {
                        "leaseID": row[0],
                        "customerID": row[1],
                        "vehicleID": row[2],
                        "startDate": row[3],
                        "endDate": row[4],
                        "type": row[5],
                    }
                    for row in cursor.fetchall()
                ]
            return leases
        except Exception as e:
            print(f"Error listing active leases: {e}")

    def list_lease_history(self) -> List[Lease]:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute("SELECT * FROM Lease")
                leases = [
                    {
                        "leaseID": row[0],
                        "customerID": row[1],
                        "vehicleID": row[2],
                        "startDate": row[3],
                        "endDate": row[4],
                        "type": row[5],
                    }
                    for row in cursor.fetchall()
                ]
            return leases
        except Exception as e:
            print(f"Error listing lease history: {e}")

    def record_payment(
        self, lease_id: int, payment_date: datetime, amount: float
    ) -> None:
        try:
            with self.connection:
                cursor = self.connection.cursor()
                cursor.execute(
                    "INSERT INTO Payment (leaseID, paymentDate, amount) VALUES (?, ?, ?)",
                    (lease_id, payment_date, amount),
                )
            print("Payment recorded successfully.")
        except Exception as e:
            print(f"Error recording payment: {e}")
