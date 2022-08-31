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
cnxn_str = ("Driver={ODBC Driver 17 for SQL Server};"
            "Server=tcp:foodallergyserver.database.windows.net,1433;"
            "Database=foodallergydb;"
            "UID=sagar_kudale;"
            "PWD=#Siddhivinayak123;"
            "Encrypt=yes;"
            "TrustServerCertificate=no;"
            "Connection Timeout=30;"
            )

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'testdemo'

mysql = MySQL(app)

selected_allergens = []

@app.route('/getstudentdetails', methods=['GET'],endpoint='getStudentDetails')
def getStudentDetails():
    if request.method == 'GET':
        print("hello world")
        allergens = []
        cnxn = pyodbc.connect(cnxn_str)
        cursor = cnxn.cursor()
        """ list = []
        #dict = {"name": "jane doe", "salary": 9000, "email": "JaneDoe@pynative.com"}
        select_sql = "SELECT * FROM student"
        res = cursor.execute(select_sql)
        print(type(res))
        for ele in res:
            list.append(ele[1])
        print(cursor.fetchall())
        """
        demo = ["dairy", "wheat"]
       # in_params = ','.join(['%s'] * len(demo))
        #sql = "SELECT allergen_name,alternative_name FROM alternative_allergen_name WHERE allergen_name IN (%s)" % in_params
        #sql = "SELECT allergen_name,alternative_name FROM alternative_allergen_name WHERE allergen_name = 'dairy' "
        #cursor.execute(sql,demo)
        #myallergens = cursor.fetchall()

        execu = cursor.execute(
            """
            Select 
             allergen_name,
             alternative_name
            From
                alternative_allergen_name
            where
             allergen_name in ({})
            """.format(','.join("?" * len(demo))), demo)

        myallergens = cursor.fetchall()

        for x, y in myallergens:
            allergens.append(y)
        #dict['name'] = list
        response = jsonify({
            "result": allergens
        })
        return response


@app.route('/form',methods=['GET'],endpoint='form')
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

@app.route('/barcode_post', methods=['POST'],endpoint='barcode_post')
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
    #in_params = ','.join(['%s'] * len(selected_allergens))
    #sql = "SELECT allergen_name,alternative_name FROM alternative_allergen_name WHERE allergen_name IN (%s)" % in_params
    #cursor.execute(sql, selected_allergens)
    #cursor.execute('''SELECT allergen_name FROM alternative_allergen_name WHERE allergen_name IN (%s)'''% in_params)
    execu = cursor.execute(
        """
        Select 
         allergen_name,
         alternative_name
        From
            alternative_allergen_name
        where
         allergen_name in ({})
        """.format(','.join("?" * len(demo))), demo)

    #myallergens = cursor.fetchall()
    myallergens = cursor.fetchall()
    print(myallergens)
    for x,y in myallergens:
        allergens.append(y)
    print(allergens)
    cursor.close()
    return allergens
    #return allergens




