from unicodedata import name
from flask import Flask, redirect, render_template, request, jsonify, abort
import os
from flask_migrate import Migrate
import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.exc import IntegrityError

garage = Flask(__name__)

CORS(garage)

database_user = os.getenv("DATABASE_USER")
database_password = os.getenv("DATABASE_PASS")
garage.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql+psycopg2://{database_user}:{database_password}@localhost/vehicles'
garage.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(garage)
migrate = Migrate(garage, db)

class Car(db.Model):
    __tablename__ = "fleet"
    id = db.Column(db.Integer, primary_key = True)
    car_name = db.Column(db.String(100), nullable = False)
    car_year = db.Column(db.Integer(), nullable = False)
    car_price = db.Column(db.Float(), nullable = False)
    car_type = db.Column(db.String(100), nullable = False)
    car_description = db.Column(db.String(250), nullable = False)
    number_plate = db.Column(db.String(80), unique=True, nullable = False)

    def __repr__(self):
        return "<Car %r>" % self.car_name

    def format(self):
        return {
            "id":self.id,
            "car_name":self.car_name,
            "car_year":self.car_year,
            "car_type":self.car_type,
            "car_price":self.car_price,
            "car_description":self.car_description,
            "car_number_plate":self.number_plate
        }

db.create_all()

@garage.route('/')
def index():
    return jsonify({"message": "Welcome to my fleet"})


@garage.route('/addcar', methods=['POST'])
def addcar():
    car_data = request.json

    car_name = car_data['car_name']
    car_type = car_data['car_type']
    car_year = car_data['car_year']
    car_price = car_data['car_price']
    car_description = car_data['car_description']
    car_number_plate = car_data['car_number_plate']

    try:
        car = Car(car_name = car_name, car_type=car_type, car_year=car_year,
                  car_price=car_price, car_description=car_description,
                  number_plate=car_number_plate)
        db.session.add(car)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        abort(409, "number plate already exists")

    #Done:TODO: add a new column to the database (number_plate), make it unique and make sure the data doesn't get saved if the same \
    # number_plate is supplied, return error message "oops!, number plate already exists"

    return jsonify({
        "success": True,
        "response": "Car successfully added"
    })

@garage.route('/getcars', methods=['GET'])
def getcars():
    all_cars = []
    cars = Car.query.all()
    
    for car in cars:
        results = {
            "car_id": car.id,
            "car_name": car.car_name,
            "car_type": car.car_type,
            "car_price": car.car_price,
            "car_year": car.car_year,
            "car_description": car.car_description
        }

        all_cars.append(results)

        #TODO: Add a getcarbyid method that returns just a car when the ID is passed

    return jsonify({
        "success": True,
        "cars": all_cars,
        "total_cars": len(cars)
    })

@garage.route('/cars/<int:id>', methods=["GET"])
def getcarbyid(id):
    gotten_car = Car.query.get(id)
    
    
    if gotten_car is None:
        abort(404)
    else:
        car = gotten_car.format()
        return jsonify({
            "car": car
        })




@garage.route('/updatecar/<int:car_id>', methods=['PATCH'])
def updatecar(car_id):
    car = Car.query.get(car_id)

    car_name = request.json['car_name']
    car_type = request.json['car_type']
    car_description = request.json['car_description']

    if car is None:
        abort(404)

    else:
        car.car_name = car_name
        car.car_type = car_type
        car.car_description = car_description
        db.session.add(car)
        db.session.commit()

    return jsonify({
        "success": True,
        "response": "Car successfully updated"
    })

@garage.errorhandler(409)
def conflict(error):
    return jsonify({
        "error": 409,
        "message":f"!oops {error}"
    })

@garage.errorhandler(404)
def not_found(error):
    return jsonify({
        "error":404,
        "message": f"{error}:  Object not found"
    })
#TODO: Add the delete endpoint

@garage.route("/cars/<int:id>", methods=["DELETE"])
def delete_car(id):
    car = Car.query.get(id)

    if car is None:
        abort(404, "Car does not exist")
    else:
        try:
            db.session.delete(car)
            db.session.commit()
            return jsonify({
                "sucess":True,
                "deleted_id":id
            })
        except Exception:
            db.session.rollback()
            abort(500, "could not delete car")

# def connection():
#     server = 'localhost' #server name
#     database = 'vehicles' #database name
#     username = 'postgres' #usrname
#     password = 'password' #password
#     conn = psycopg2.connect(host=server, database=database, user=username, password=password)
#     return conn

# @garage.route('/')
# def main():
#     cars = []
#     conn = connection()
#     cursor = conn.cursor()
#     cursor.execute("SELECT * FROM LiverpoolCars")
#     for row in cursor.fetchall():
#         cars.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
#     conn.close()
#     return render_template("carlist.html", cars = cars)

# @garage.route('/addcar', methods=['GET', 'POST'])
# def addcar():
#     if request.method == 'GET':
#         return render_template("addcar.html", car = {})
#     if request.method == 'POST':
#         id = int(request.form["id"])
#         name = request.form["name"]
#         year = int(request.form["year"])
#         price = float(request.form["price"])
#         conn = connection()
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO LiverpoolCars (id, name, year, price) VALUES (%s, %s, %s, %s)", (id, name, year, price))
#         conn.commit()
#         conn.close()
#         return redirect('/')
    
# @garage.route('/updatecar/<int:id>', methods=['GET', 'POST'])
# def updatecar(id):
#     cr = []
#     conn = connection()
#     cursor = conn.cursor()
#     if request.method == 'GET':
#         cursor.execute("SELECT * FROM LiverpoolCars WHERE id = %s", (str(id)))
#         for row in cursor.fetchall():
#             cr.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
#         conn.close()
#         return render_template("addcar.html", car = cr[0])
#     if request.method == "POST":
#         name = request.form["name"]
#         year = int(request.form["year"])
#         price = float(request.form["price"])
#         cursor.execute("UPDATE LiverpoolCars SET name = %s, price = %s, year = %s where id = %s", (name, price, year, id))
#         conn.commit()
#         conn.close()
#         return redirect('/')

# @garage.route('/deletecar/<int:id>')
# def deletecar(id):
    # conn = connection()
    # cursor = conn.cursor()
    # cursor.execute("DELETE FROM LiverPoolCars WHERE id = %s", (str(id)))
    # conn.commit()
    # conn.close()
    # return redirect('/')
    

if __name__ == '__main__':
    garage.run(debug=True)
