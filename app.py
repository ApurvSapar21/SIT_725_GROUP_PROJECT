import openfoodfacts.products
from flask import Flask,render_template, request,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
#from PIL import Image
#from pytesseract import pytesseract
import mysql.connector
import requests
import json
import base64
import io
import pyodbc
app = Flask(__name__)
CORS(app)

# Obtain connection string information from the portal

config = {
  'host':'foodallerserver.mysql.database.azure.com',
  'port': '3306',
  'user':'sagar_kudale',
  'password':'#Siddhivinayak123',
  'database':'demo',
  'ssl_ca': 'D:/DigiCertGlobalRootG2.crt.pem',
  'ssl_disabled':'False'
}

cnx = mysql.connector.connect(user="sagar_kudale", password="#Siddhivinayak123",
                              host="foodallerserver.mysql.database.azure.com", port=3306,
                              database="demo", ssl_ca="D:/DigiCertGlobalRootG2.crt.pem",
                              ssl_disabled=False)

cnxn_str = ("Driver={ODBC Driver 17 for SQL Server};"
            "Server=tcp:foodallergyserver.database.windows.net,1433;"
            "Database=foodallergydb;"
            "UID=sagar_kudale;"
            "PWD=#Siddhivinayak123;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
            )

"""
try: 
   conn = mysql.connector.connect(**config)
   print("Connection established")
except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Something is wrong with the user name or password")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Database does not exist")
  else:
    print(err)
else:
  cursor = conn.cursor()
"""
# Create table
#cursor.execute("CREATE TABLE inventory (id serial PRIMARY KEY, name VARCHAR(50), quantity INTEGER);")
print("Finished creating table.")

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'testdemo'

mysql = MySQL(app)

selected_allergens = []

@app.route('/getstudentdetails', methods=['GET'])
def getStudentDetails():
    if request.method == 'GET':
        print("hello world")
        cnxn = pyodbc.connect(cnxn_str)
        cursor = cnxn.cursor()
        list = []
        #dict = {"name": "jane doe", "salary": 9000, "email": "JaneDoe@pynative.com"}
        select_sql = "SELECT * FROM student"
        res = cursor.execute(select_sql)
        print(type(res))
        for ele in res:
            list.append(ele[1])
        print(cursor.fetchall())
        #dict['name'] = list
        response = jsonify({
            "result": list
        })
        return response


@app.route('/form',methods=['GET'])
def form():
    code = '5000396015935'
    temp_url = "https://world.openfoodfacts.org/api/v0/product.json"
    url = '/'.join([temp_url, code])
    myResponse = requests.get(url, verify=True)
    # print (myResponse.status_code)

    # For successful API call, response code will be 200 (OK)
    if (myResponse.ok):
        # Loading the response data into a dict variable
        # json.loads takes in only binary or string variables so using content to fetch binary content
        # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
        jData = json.loads(myResponse.content)

        print("The response contains {0} properties".format(len(jData)))
        print("\n")
        print(jData)
    else:
        # If response code is not ok (200), print the resulting http error code with description
        myResponse.raise_for_status()
    pro = openfoodfacts.products.get_product('5000396015935')
    print(type(pro['product']['ingredients_hierarchy']))
    return str(pro['product']['ingredients_hierarchy'])


@app.route('/getinfo', methods=['GET'])
def getInfo():
    if request.method == 'GET':
        list = ["sad","rfe"]
        return list

@app.route('/barcode_post', methods=['POST'])
@cross_origin()
def barcode_post():
    if request.method == 'POST':
        print(selected_allergens)
        barcode = request.json
        print(barcode)
        barcode_data = barcode['barcode']
        code_id = barcode_data
        temp_url = "https://world.openfoodfacts.org/api/v0/product.json"
        url = '/'.join([temp_url, code_id])
        myResponse = requests.get(url, verify=True)
        # print (myResponse.status_code)

        # For successful API call, response code will be 200 (OK)
        if (myResponse.ok):
            # Loading the response data into a dict variable
            # json.loads takes in only binary or string variables so using content to fetch binary content
            # Loads (Load String) takes a Json file and converts into python data structure (dict or list, depending on JSON)
            jData = json.loads(myResponse.content)

            print("The response contains {0} properties".format(len(jData)))
            print("\n")
            print(jData)

        else:
            # If response code is not ok (200), print the resulting http error code with description
            myResponse.raise_for_status()

    alternate_allergens = getAllergendata()
    barcode_allergens = jData['product']['ingredients_hierarchy']

    barcode_allergens = [x.split(':')[1] for x in barcode_allergens]
    print(barcode_allergens)
    for barllergen in barcode_allergens:
        if barllergen in alternate_allergens:
            return "Avoid having the product"
    return "go ahead and have the product"

    #return jData['product']['ingredients_hierarchy']

def getAllergendata():
    allergens = []
    demo = ["dairy","wheat"]
    cnxn = pyodbc.connect(cnxn_str)
    cursor = cnxn.cursor()
    #cursor = mysql.connection.cursor()
    in_params = ','.join(['%s'] * len(selected_allergens))
    sql = "SELECT allergen_name,alternative_name FROM alternative_allergen_name WHERE allergen_name IN (%s)" % in_params
    cursor.execute(sql, selected_allergens)
    #cursor.execute('''SELECT allergen_name FROM alternative_allergen_name WHERE allergen_name IN (%s)'''% in_params)
    myallergens = cursor.fetchall()
    print(myallergens)
    for x,y in myallergens:
        allergens.append(y)
    print(allergens)
    cursor.close()
    response = jsonify({
        "allergens": allergens
    })
    return response
    #return allergens

@app.route('/user_allergies', methods=['POST'])
@cross_origin()
def user_allergies_post():

    if request.method == 'POST':
        user_data = ['wheat','sugar','salt','milk']
        product_ingredent = ['water','mayo']
        user_allergies = request.json
        print(user_allergies)
        #allergies_data = user_allergies['allergies']
        for ele in user_allergies['allergies']:
            if ele['Checked'] == True:
                selected_allergens.append(ele['Name'])
    print(selected_allergens)

        #print("allergies data" + allergies_data)
    return "none"


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'GET':
        return "Login via the login Form"

    if request.method == 'POST':
        id = request.form['id']
        print(id)
        name = request.form['name']
        cursor = mysql.connection.cursor()
        cursor.execute(''' INSERT INTO student VALUES(%s,%s)''', (id, name))
        mysql.connection.commit()
        cursor.close()
        return f"Done!!"