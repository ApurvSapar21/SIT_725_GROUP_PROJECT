import openfoodfacts.products
from flask import Flask,render_template, request,jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from flask_bootstrap import Bootstrap
#from PIL import Image
#from pytesseract import pytesseract
import mysql.connector
import requests
import json
import base64
import io
import pyodbc
app = Flask(__name__,template_folder='templates',static_folder='static')
CORS(app)
Bootstrap(app)



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
product_barcode = []

@app.route('/')
def HomePagev():
    opening_slogan = 'As a Parent of Children with Food Allergies,\nShopping Has Never been Easier!'
    button_txt="Click to start scanning"
    return render_template('home-v2.html',result = opening_slogan,
                           btn_txt = button_txt)


@app.route('/Food_sub',endpoint='Food_sub')
def get_food_sub():
    return render_template("Food_sub.html")

@app.route('/wheat',endpoint='wheat')
def get_wheat():
    return render_template("wheat.html")

@app.route('/dairy',endpoint='dairy')
def get_dairy():
    return render_template("dairy.html")

@app.route('/egg',endpoint='egg')
def get_egg():
    return render_template("egg.html")

@app.route('/shellfish',endpoint='shellfish')
def get_shellfish():
    return render_template("shellfish.html")

@app.route('/soy',endpoint='soy')
def get_soy():
    return render_template("soy.html")

@app.route('/sesame',endpoint='sesame')
def get_sesame():
    return render_template("sesame.html")

@app.route('/treenut',endpoint='treenut')
def get_treenut():
    return render_template("treenut.html")

@app.route('/peanut',endpoint='peanut')
def get_peanut():
    return render_template("peanut.html")



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

@app.route('/barcode_post', methods=['POST','GET'],endpoint='barcode_post')
@cross_origin()
def get_barcode_post():
    product_barcode.clear()
    #if (request.method == 'POST'):
    print(selected_allergens)
    barcode = request.json
    print(barcode)
    barcode_data = barcode['barcode']
    code_id = barcode_data
    product_barcode.append(code_id)
    print(product_barcode)

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
        print(myResponse.raise_for_status())
    tea_sugar = teaspoons_sugar()
    teaspoons = tea_sugar[0]
    compare_to_intake = tea_sugar[1]
    sugar = tea_sugar[2]
    alternate_allergens = getAllergendata()
    try:
        barcode_allergens = jData['product']['ingredients_hierarchy']
    except Exception as e:
        return jsonify(
            {"result":"product not found in Database",
            "teaspoons": teaspoons,
            "compare_to_intake": compare_to_intake,
            "sugar": sugar
             })

    barcode_allergens = [x.split(':')[1] for x in barcode_allergens]
    print(barcode_allergens)
    result = ""
    for barllergen in barcode_allergens:
        if barllergen in alternate_allergens:
            return jsonify({"result":"Avoid having the product"})
            #result = "Avoid having the product"
    result = "go ahead and have the product"
            #return "Avoid having the product"
    #return "go ahead and have the product"
    response = jsonify({
        "result": result,
        "teaspoons": teaspoons,
        "compare_to_intake" : compare_to_intake,
        "sugar":sugar
    })

    return response

    #return jData['product']['ingredients_hierarchy']

@app.route('/clearallergens', methods=['POST','GET'],endpoint='clearallergens')
@cross_origin()
def clearAllergens():
    selected_allergens.clear()
    if not selected_allergens:
        return jsonify({"result": "cleared"})
    return jsonify({"result": "selected allergens are not empty yet"})


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
        """.format(','.join("?" * len(selected_allergens))), selected_allergens)
    #selected_allergens.clear()
    #selected_allergens = []
    #myallergens = cursor.fetchall()
    myallergens = cursor.fetchall()
    print(myallergens)
    for x,y in myallergens:
        allergens.append(y)
    print(allergens)
    cursor.close()
    return allergens
    #return allergens

@app.route('/user_allergies', methods=['POST'])
@cross_origin()
def user_allergies_post():
    if request.method == 'POST':
        user_allergies = request.json
        print(user_allergies)
        for ele in user_allergies['allergies']:
            if ele['Checked'] == True:
                selected_allergens.append(ele['Name'])
    print(selected_allergens)
    return "none"


def get_salt():
    #barcode number as string
    print(product_barcode)

    try:
        product_s = openfoodfacts.products.get_product(product_barcode[0])
        salt_unit = product_s['product']['nutriments']['salt_unit']
        if salt_unit == 'g':
            salt_intake = product_s['product']['nutriments']['salt_serving']
        elif salt_unit == 'mg':
            salt_intake = (product_s['product']['nutriments']['salt_serving'])*1000
        return salt_intake
    except KeyError:
        return 0

@app.route('/age_range', methods=['POST'])
def salt_comparison():
    age_ranges = request.json
    print(age_ranges)
    age_range = age_ranges['age']
    salt_per_serving = get_salt()
    if salt_per_serving == 0:
        response = jsonify({
            "times": 0,
            "age_range": 0
        })
        return response
    else:
        if age_range == '1-3 years':
            times = salt_per_serving/0.75*100
        elif age_range == '4-8 years':
            times = salt_per_serving/1.2*100
        elif age_range == '9-13 years':
            times = salt_per_serving/1.5*100
        response = jsonify({
            "times": times,
            "age_range": age_range
        })
        #return str(times) + ' % of the recommended daily intake of salt for a child within the age '+ age_range
        product_barcode.clear()
        return response

def get_sugar():
    #barcode number as string
    product_s = openfoodfacts.products.get_product(product_barcode[0])
    try:
        sugar_unit = product_s['product']['nutriments']['sugars_unit']
        if sugar_unit == 'g':
            sugar_intake = product_s['product']['nutriments']['sugars_serving']
        elif sugar_unit == 'mg':
            sugar_intake = (product_s['product']['nutriments']['sugars_serving'])*1000
        return sugar_intake
    except KeyError:
        #return "In our data,the product does not show sugars per serving"
        return 0

def teaspoons_sugar():
    tea_sugar_arr = []
    sugar = get_sugar()
    #each teaspoon has about 4.2g of sugar
    if sugar != 0:
        teaspoons = sugar / 4.2
        compare_to_intake = sugar / 20 * 100
        tea_sugar_arr.append(teaspoons)
        tea_sugar_arr.append(compare_to_intake)
        tea_sugar_arr.append(sugar)
    else:
        tea_sugar_arr.append(0)
        tea_sugar_arr.append(0)
        tea_sugar_arr.append(0)
    #return 'Number of teaspoons:',teaspoons,compare_to_intake, '% the required daily sugar intake for a child'
    return tea_sugar_arr


