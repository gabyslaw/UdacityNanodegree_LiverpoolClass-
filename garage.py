from unicodedata import name
from flask import Flask, redirect, render_template, request
import psycopg2

garage = Flask(__name__)

def connection():
    server = 'localhost' #server name
    database = 'vehicles' #database name
    username = 'postgres' #usrname
    password = 'password' #password
    conn = psycopg2.connect(host=server, database=database, user=username, password=password)
    return conn

@garage.route('/')
def main():
    cars = []
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM LiverpoolCars")
    for row in cursor.fetchall():
        cars.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
    conn.close()
    return render_template("carlist.html", cars = cars)

@garage.route('/addcar', methods=['GET', 'POST'])
def addcar():
    if request.method == 'GET':
        return render_template("addcar.html", car = {})
    if request.method == 'POST':
        id = int(request.form["id"])
        name = request.form["name"]
        year = int(request.form["year"])
        price = float(request.form["price"])
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO LiverpoolCars (id, name, year, price) VALUES (%s, %s, %s, %s)", (id, name, year, price))
        conn.commit()
        conn.close()
        return redirect('/')
    
@garage.route('/updatecar/<int:id>', methods=['GET', 'POST'])
def updatecar(id):
    cr = []
    conn = connection()
    cursor = conn.cursor()
    if request.method == 'GET':
        cursor.execute("SELECT * FROM LiverpoolCars WHERE id = %s", (str(id)))
        for row in cursor.fetchall():
            cr.append({"id": row[0], "name": row[1], "year": row[2], "price": row[3]})
        conn.close()
        return render_template("addcar.html", car = cr[0])
    if request.method == "POST":
        name = request.form["name"]
        year = int(request.form["year"])
        price = float(request.form["price"])
        cursor.execute("UPDATE LiverpoolCars SET name = %s, price = %s, year = %s where id = %s", (name, price, year, id))
        conn.commit()
        conn.close()
        return redirect('/')

@garage.route('/deletecar/<int:id>')
def deletecar(id):
    conn = connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM LiverPoolCars WHERE id = %s", (str(id)))
    conn.commit()
    conn.close()
    return redirect('/')
    

if __name__ == '__main__':
    garage.run(debug=True)