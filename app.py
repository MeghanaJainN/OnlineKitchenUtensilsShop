from flask import Flask, redirect, render_template, flash, url_for
from flask import request
import mysql.connector as mysql
import re

app = Flask(__name__, template_folder="template", static_folder="images")
app.secret_key = "super secret key"


@app.route('/', methods=['GET'])
def MyhomeRoot():
    return render_template('login.html')


def is_valid_password(password):
    # Minimum length requirement
    if len(password) < 8:
        return False

    # Complexity requirements
    if not re.search(r'[A-Z]', password) or \
       not re.search(r'[a-z]', password) or \
       not re.search(r'[0-9]', password) or \
       not re.search(r'[!@#\$%\^&\*]', password):
        return False

    # Common word or pattern check
    common_passwords = ["password", "123456", "qwerty"]
    if password.lower() in common_passwords:
        return False

    # User information check (e.g., username, email)
    if "username" in password.lower() or "email" in password.lower():
        return False
    return True


@app.route('/My_Login_Process', methods=["POST"])
def My_Login_Process():
    uid = request.form["username"]
    pwd = request.form["password"]
    if not is_valid_password(pwd):
        return render_template('error.html', message="Invalid password. Please follow password requirements.")
    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root", password="Megha@2002", use_pure=True)
        sql = "Select username, password From login where username = " + "'" + uid + "'"
        mycursor = db_connect.cursor()
        mycursor.execute(sql)
        cno = mycursor.fetchall()
        res = [tuple(str(item) for item in t) for t in cno]
        print(res)
    except Exception as err:
        print(err)
        return render_template('error.html')
    if len(res) == 0:
        status = 0
        return render_template('error.html')
    else:
        usrid = res[0][0]
        passwd = res[0][1]
        if (usrid == uid and usrid == 'megha' and pwd == passwd):
            return render_template('admin.html', usrid=usrid)
        elif (usrid == uid and pwd == passwd):

            return render_template('home.html', usrid=usrid)
        else:
            return render_template('home.html', usrid=usrid)


@app.route("/My_sign_process", methods=['POST'])
def My_sign_process():
    uid = request.form["username"]
    eid = request.form["email"]
    pwd = request.form["password"]

    if not is_valid_password(pwd):
        return render_template('error.html', message="Invalid password. Please follow password requirements.")
    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root", passwd="Megha@2002", use_pure=True)
        sql = "INSERT INTO signup(username,email,password) VALUES(" + \
            "'" + uid + "'" + "," + "'" + eid + "'" + "," + "'"+pwd+"'" + ")"
        sql1 = "INSERT INTO login(username,password) VALUES(" + \
            "'" + uid + "'" + "," + "'" + pwd + "'" + ")"
        mycursor = db_connect.cursor()
        mycursor.execute(sql)
        mycursor.execute(sql1)
        db_connect.commit()
        return render_template('home.html')
    except Exception as err:
        print(err)
        return render_template('error.html')


@app.route('/products', methods=['GET'])
def products():
    return render_template("products.html")


@app.route('/productss', methods=['POST'])
def productss():
    return render_template("products.html")


@app.route('/home', methods=['GET'])
def home():
    return render_template("home.html")


def fetch_product_data():
    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root",
            passwd="Megha@2002", use_pure=True)

        cursor = db_connect.cursor()
        query = "SELECT * FROM products"
        cursor.execute(query)
        cdata = cursor.fetchall()

        cursor.close()
        db_connect.close()

        return cdata
    except Exception as err:
        print(err)
        return None


@app.route('/add_to_db', methods=['POST'])
def add_to_db():
    product_name = request.form['product_name']
    product_price = float(request.form['product_price'])
    product_quantity = int(request.form['product_quantity'])

    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root",
            passwd="Megha@2002", use_pure=True)

        if product_quantity <= 0:
            raise ValueError("Quantity must be greater than 0")
            # username = session.get('username')

        total_price = product_price * product_quantity

        sql = "INSERT INTO products (name, price, quantity, totalprice) VALUES (%s,%s, %s, %s)"
        values = (product_name, product_price, product_quantity, total_price)
        mycursor = db_connect.cursor()
        mycursor.execute(sql, values)
        db_connect.commit()

        # Fetch product data using the helper function
        cdata = fetch_product_data()
        sumt = sub_total()

        return render_template("cart.html", cdata=cdata, sumt=sumt)
    except Exception as err:
        print(err)
        return render_template('error.html', message=str(err))


'''@app.route('/add_to_db', methods=['POST'])
def add_to_db():
    product_name = request.form['product_name']
    # Convert the price to a float
    product_price = float(request.form['product_price'])
    # Convert the quantity to an integer
    product_quantity = int(request.form['product_quantity'])

    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root", passwd="Megha@2002", use_pure=True)

        if product_quantity <= 0:
            raise ValueError("error.html")

        total_price = product_price * product_quantity

        sql = "INSERT INTO products (name, price, quantity,totalprice) VALUES (%s, %s, %s, %s)"
        values = (product_name, product_price, product_quantity, total_price)

        mycursor = db_connect.cursor()
        mycursor.execute(sql, values)

        cdata = fetch_product_data()
        sumt = sub_total()

        db_connect.commit()
        return render_template("cart.html", cdata=cdata, sumt=sumt)
    except Exception as err:
        print(err)
        return render_template('error.html', message=str(err))'''


@app.route('/cart', methods=['POST'])
def cart():
    return render_template("cart.html")


@app.route('/load', methods=['POST'])
def load():
    return render_template("home.html")


@app.route('/deletes', methods=['POST'])
def deletes():
    cdata = []
    sumt = []
    try:
        # Get the product name from the form
        products_name = request.form.get('products_name')
        db = mysql.connect(
            host="localhost", database="paakashala", user="root", passwd="Megha@2002", use_pure=True)

        # Create a cursor to interact with the database
        cursor = db.cursor()
        print("Product Name:", products_name)

        # Execute an SQL query to delete the row by product name
        sql = "DELETE FROM paakashala.products WHERE name = %s"
        cursor.execute(sql, (products_name,))
        sql1 = "SELECT name,price,quantity,totalprice FROM products "

        cursor.execute(sql1)
        cdata = cursor.fetchall()
        query = "SELECT SUM(totalprice) FROM products"
        cursor.execute(query)
        sumt = cursor.fetchone()[0]
        db.commit()
      # Close thersor
        cursor.close()

        flash('Row removed successfully', 'success')
    except Exception as e:
        db.rollback()
        flash('An error occurred while removing the row: ' + str(e), 'error')

    return render_template("cart.html", cdata=cdata, sumt=sumt)


def sub_total():
    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root", passwd="Megha@2002", use_pure=True)

        cursor = db_connect.cursor()
        query = "SELECT SUM(totalprice) FROM products"
        cursor.execute(query)
        sumt = cursor.fetchone()[0]

        cursor.close()
        db_connect.close()

        return sumt
    except Exception as err:
        print(err)
        return None


@app.route('/checkout', methods=['POST'])
def checkout():
    try:
        db_connect = mysql.connect(
            host="localhost", database="paakashala", user="root", passwd="Megha@2002", use_pure=True)
        query = "DELETE FROM products"
        mycursor = db_connect.cursor()
        mycursor.execute(query)
        db_connect.commit()

        return render_template("load.html")
    except Exception as err:
        print(err)
        return render_template('error.html')


if __name__ == '__main__':
    app.run(debug=True)
