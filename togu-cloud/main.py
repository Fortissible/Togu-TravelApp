import os
import sqlalchemy
from flask import Flask, request
import json
import datetime
import base64


app = Flask(_name_)

connection_name = ""
db_name = ""
db_user = ""
db_password = ""
driver_name = ''
query_string = dict({"unix_socket": "/cloudsql/{}".format(connection_name)})

kode_rahasia = "gagasmanusiasilver"

def generate_token(email):
    datenya = datetime.datetime.now()
    result = (str(email)+"|"+str(datenya)+"|"+kode_rahasia).encode("utf-8")
    bs64 = base64.b64encode(result)
    return bs64

db = sqlalchemy.create_engine(
      sqlalchemy.engine.url.URL(
        drivername=driver_name,
        username=db_user,
        password=db_password,
        database=db_name,
        query=query_string,
      ),
      pool_size=5,
      max_overflow=2,
      pool_timeout=30,
      pool_recycle=1800
    )

@app.route("/getinfouser", methods=["POST", "GET"])
def getinfouser():
    table_name = 'user' 
    if request.method == "POST":
        req = request.get_json()
        token = req['token']
        
        base64_bytes = token.encode('ascii')
        message_bytes = base64.b64decode(base64_bytes)
        decodedToken = message_bytes.decode('ascii')


        splitToken = decodedToken.split("|")

        if splitToken[-1] == kode_rahasia:
            email = splitToken[0]
        else:
            return json.dumps({"error": "Wrong Token"})
        

        querysql = sqlalchemy.text('select * from {} where email = "{}"'.format(table_name, email))
        try:
            with db.connect() as conn:
                result = conn.execute(querysql)
                return json.dumps([dict(x) for x in result])

        except Exception as e:                
            return 'Error: {}'.format(str(e))
    else:
        return "Gunakan POST"
    

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        req = request.get_json()
        email = req['email']
        password = req['password']
        table_name = 'user' 
        querysql = sqlalchemy.text('select * from {} where email = "{}" and password = "{}"'.format(table_name, email, password))
        try:
            with db.connect() as conn:
                result = conn.execute(querysql)
                row = result.fetchall()
                if len(row) > 0:
                    return json.dumps({"login": "sukses", "token": str(generate_token(email))})
                else :
                    return json.dumps({"login": "gagal"})

        except Exception as e:                
            return 'Error: {}'.format(str(e))
    else:
        return "Gunakan POST"

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        req = request.get_json()
        email = req['email']
        password = req['password']
        nama = req['nama']
        notelp = req['notelp']
        table_name = 'user'
        role = req['role']
        username = req['username']
        gender = req['gender']

        if role == "guide":
            rating = 0
            harga = 0
            querysql = sqlalchemy.text('insert into {} (email, password, nama, username, notelp, role, rating, harga, gender) values ("{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(table_name, email, password, nama, username, notelp, role, rating, harga, gender))
        else:
            querysql = sqlalchemy.text('insert into {} (email, password, nama, username, notelp, role, gender) values ("{}", "{}", "{}", "{}", "{}", "{}", "{}")'.format(table_name, email, password, nama, username, notelp, role, gender))

        try:
            with db.connect() as conn:
                conn.execute(querysql)
        except Exception as e:
            return json.dumps({"error": str(e),"message": "Registrasi Gagal"})
        return json.dumps({"error": "false","message": "Registrasi Sukses"}) 
    else:
        return "Gunakan POST"



@app.route("/getwisata", methods=["GET", "POST"])
def getwisata():

        table_name = 'lokasi_wisata' 

        param = request.args.get('search')

        if param:
            querysql = sqlalchemy.text('SELECT * from {} WHERE nama LIKE "%{}%"'.format(table_name, param))               
        else:
            querysql = sqlalchemy.text('SELECT * from {}'.format(table_name))
        
        try:
            with db.connect() as conn:
                result = conn.execute(querysql)
                return json.dumps([dict(x) for x in result])

        except Exception as e:                
            return 'Error: {}'.format(str(e))


@app.route("/getobjek", methods=["GET", "POST"])
def getobjek():
        param = request.args.get('search')
        table_name = 'objek_wisata' 

        querysql = sqlalchemy.text('select * from {} WHERE lokasi LIKE "%{}%"'.format(table_name, param))
        
        try:
            with db.connect() as conn:
                result = conn.execute(querysql)
                return json.dumps([dict(x) for x in result])

        except Exception as e:                
            return 'Error: {}'.format(str(e))

@app.route("/findtourguide", methods=["GET", "POST"])
def findtourguide():
        param = request.args.get('search')
        table_name = 'user' 

        if param:
            querysql = sqlalchemy.text('select iduser, nama, email ,notelp, rating, harga, gender, url_image  from {} WHERE role = "guide" and nama LIKE "%{}%"'.format(table_name, param))
        else:
            querysql = sqlalchemy.text('select iduser, nama, email ,notelp, rating, harga, gender, url_image  from {} WHERE role = "guide"'.format(table_name))    
        
        try:
            with db.connect() as conn:
                result = conn.execute(querysql)
                return json.dumps([dict(x) for x in result])

        except Exception as e:                
            return 'Error: {}'.format(str(e))





if _name_ == "_main_":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
