from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS
from config import config
from random import randint
from time import sleep

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})
conexion=MySQL(app)

# ----- USUARIOS -----

#Registro de sesión
@app.route('/registrar', methods=['POST'])
def register():
    try:
        user = read_user_bd_byMail(request.json['Correo'])
        if user != None:
            return jsonify({'mensaje':"Alumno ya existe, no se puede duplicar", 'exito': False})
        else:
            cursor = conexion.connection.cursor()
            sql = """
                INSERT INTO users 
                (Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono)
                VALUES (%s, %s, %s, %s, %s, '', '', '')
            """
            valores = (
                request.json['Correo'],
                request.json['Username'],
                request.json['Nombre'],
                request.json['Contrasena'],
                request.json['FechaNac']
            )

            cursor.execute(sql, valores)
            conexion.connection.commit()

            createPersonalData(cursor.lastrowid)

            return jsonify({'mensaje': "Usuario registrado", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error "+str(ex)+" "+str(request.json), 'exito': False})

#login
@app.route('/login', methods=['POST'])
def login():
    try:
        user = read_user_bd_byMail(request.json['Correo'])
        if user == None:
            return jsonify({'mensaje':"No se ha encontrado usuario con este correo", 'exito': False})
        else:
            if request.json['Contrasena'] != user['Contrasena']:
                return jsonify({'mensaje': "Contraseña incorrecta", 'exito': False})
            else:
                return jsonify({'user':user, 'mensaje': "Inicio de sesión exitoso", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error "+str(ex), 'exito': False})

#listar usuarios
@app.route('/busqueda-de-amigos', methods=['GET'])
def search():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_User, Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono FROM users"
        cursor.execute(sql)
        data = cursor.fetchall()
        users=[]
        for row in data:
            user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8]}
            users.append(user)
        return jsonify({'users': users, 'mensaje':"Usuarios encontrados", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar alumnos:{}"+str(ex), 'exito':False})

#mostrar usuario específico
@app.route('/perfil/<id>', methods=['GET'])
def perfil(id):
    try:
        user = read_user_bd(id)
        return jsonify({'user': user, 'mensaje':"Usuario encontrado", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar alumnos:{}"+str(ex), 'exito':False})

#Update
@app.route('/perfil/<id>', methods=['PUT'])
def perfilUpdate(id):
    try:
        user = read_user_bd(id)
        if user != None:
            cursor = conexion.connection.cursor()
            sql = """UPDATE users SET Correo = '{0}', Username = '{1}', Nombre = '{2}', Descripcion = '{3}', 
            Telefono = '{4}', Foto = '{5}' WHERE ID_User = {6}""".format(request.json['Correo'], request.json['Username'], request.json['Nombre'], request.json['Descripcion']
                                                    , request.json['Telefono'], request.json['Foto'], id)
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': "Perfil actualizado", 'exito': True})
        else:
            return jsonify({'mensaje': "Perfil no encontrado", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0} ".format(ex), 'exito': False})

#Delete
@app.route('/perfil/<id>', methods=['DELETE'])
def perfilDelete(id):
    try:
        user = read_user_bd(id)
        if user != None:
            cursor = conexion.connection.cursor()
            sql = "DELETE FROM users WHERE ID_User = {0}".format(id)
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': "Perfil eliminado correctamente", 'exito': True})
        else:
            return jsonify({'mensaje': "Perfil no encontrado", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

# ----- REPORTES -----

@app.route('/reporte', methods=['POST'])
def createReport():
    try:
        cursor = conexion.connection.cursor()
        sql = """
            INSERT INTO reports 
            (Correo, Tema, Descripcion, Imagen)
            VALUES (%s, %s, %s, %s)
        """

        valores = (
            request.json['Correo'],
            request.json['Tema'],
            request.json['Descripcion'],
            request.json['Imagen']
        )
        cursor.execute(sql, valores)
        conexion.connection.commit()
        return jsonify({'mensaje': "Reporte registrado", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

# ----- RECUPERACIÓN ----- 

@app.route('/recuperar-cuenta', methods=['POST'])
def createRecoveryRequest():
    try:
        cursor = conexion.connection.cursor()
        sql = """
            INSERT INTO recovery 
            (Correo, Contrasena)
            VALUES (%s, %s)
        """

        valores = (
            request.json['Correo'],
            request.json['Contrasena']
        )
        cursor.execute(sql, valores)
        conexion.connection.commit()
        return jsonify({'mensaje': "Peticiion de recuperación registrada", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

# ----- AUTENTICACIÓN ----- 

@app.route('/codigoveri', methods=['POST'])
def createAuthRequest():
    try:
        cursor = conexion.connection.cursor()
        sql = """
            INSERT INTO auth 
            (ID_User, Code)
            VALUES (%s, %s)
        """

        valores = (
            request.json['ID_User'],
            randint(100000, 999999)
        )
        cursor.execute(sql, valores)
        conexion.connection.commit()
        deleteAfterDelay(cursor.lastrowid)
        return jsonify({'mensaje': "Peticiion de recuperación registrada", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

def deleteAfterDelay(id):
    sleep(900)
    try:
        cursor = conexion.connection.cursor()
        sql = "DELETE FROM auth WHERE ID_Auth = {0}".format(id)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': "Codigo eliminado correctamente", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

#Falta función para validar código

# ----- DATOS PERSONALES -----

@app.route('/pago/<id_user>', methods=['PUT'])
def updatePersonalData(id_user):
    try:
        personal_data = read_personal_data_bd(id_user)
        if personal_data != None:
            cursor = conexion.connection.cursor()
            sql = """UPDATE personal_data SET Tipo = '{0}', NumeroTarjeta = '{1}', Vigencia = '{2}', CVC = {3}, 
            NombrePropietario = '{4}', ApellidoPropietario = '{5}', Pais = '{6}', CP = {7} WHERE ID_User = {8}""".format(
            request.json['Tipo'], request.json['NumeroTarjeta'], request.json['Vigencia'], request.json['CVC']
            , request.json['NombrePropietario'], request.json['ApellidoPropietario'], request.json['Pais'], request.json['CP'], id_user)
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': "Datos personales actualizados", 'exito': True})
        else:
            return jsonify({'mensaje': "Usuario no encontrado", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0} ".format(ex), 'exito': False})        

def createPersonalData(id_user):
    try:
        cursor = conexion.connection.cursor()
        sql = """INSERT INTO personal_data (ID_User, Tipo, NumeroTarjeta, Vigencia, CVC, NombrePropietario, ApellidoPropietario, Pais, CP)
        values ({0}, '', '', '', 0, '', '', '', 0)""".format(id_user)
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': "Personal Data creado", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

# ----- VENTAS -----

@app.route('/sales', methods=['POST'])
def registerSale():
    try:
        if read_user_bd(request.json['ID_User']) == None or read_game_bd(request.json['ID_Juego']) == None:
            return jsonify({'mensaje': "No se ha encontrado un usuario o juego", 'exito': False})

        cursor = conexion.connection.cursor()
        sql = """INSERT INTO sales ('ID_User', 'Fecha', 'ID_Juego', 'PrecioTotal', 'Descuento')""".format(
            request.json['ID_User'], request.json['Fecha'], request.json['ID_Juego'], request.json['PrecioTotal'], request.json['Descuento'])
        
        cursor.execute(sql)
        conexion.connection.commit()
        return jsonify({'mensaje': "Personal Data creado", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

@app.route('/historial/<id_user>', methods=['GET'])
def viewSalesHistory(id_user):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_Sale, ID_User, Fecha, ID_Juego, PrecioTotal, Descuento FROM sales WHERE ID_User = {0}""".format(id_user)
        cursor.execute(sql)
        data = cursor.fetchall()
        sales=[]
        for row in data:
            sale = {'ID_Sale': row[0], 'ID_User': row[1],
                      'Fecha': row[2], 'ID_Juego': row[3],
                      'PrecioTotal': row[4], 'Descuento': row[5]}
            sales.append(sale)
        return jsonify({'sales': sales, 'mensaje':"Usuarios encontrados", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar alumnos:{}"+str(ex), 'exito':False})

# ----- AMIGOS -----



# ----- JUEGOS -----

#listar juegos
@app.route('/catalogo', methods=['GET'])
def catalog():
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_Juego, Nombre, Descripcion, Imagen, Precio, Descuento, Genero, Plataforma, Clasificación FROM games"
        cursor.execute(sql)
        data = cursor.fetchall()
        games=[]
        for row in data:
            game = {'ID_Juego': row[0], 'Nombre': row[1], 'Descripcion': row[2],
                    'Imagen': row[3], 'Precio': row[4], 'Descuento': row[5], 
                    'Genero': row[6], 'Plataforma': row[7], 'Clasificacion': row[8]}
            games.append(game)
        return jsonify({'games': games, 'mensaje': "Mostrando juegos", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar juegos:{}"+str(ex), 'exito': False})

#listar juego especifico
@app.route('/catalogo/<id>', methods=['GET'])
def game(id):
    try:
        game = read_game_bd(id)
        if game != None:
            return jsonify({'game': game, 'mensaje': "Juego encontrado", 'exito': True})
        else:
            return jsonify({'mensaje': "Juego no encontrado", 'exito': False})
    except Exception as ex:
        return jsonify({'mensaje': "Error", 'exito': False})

# ----- lecturas individuales -----
def read_user_bd(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_User, Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono FROM users WHERE ID_User = {0}".format(id)
        cursor.execute(sql)
        datos = cursor.fetchone()

        if datos != None:
            user = {'ID_User': datos[0], 'Correo': datos[1],
                      'Username': datos[2], 'Nombre': datos[3],
                      'Contrasena': datos[4], 'FechaNac': datos[5],
                      'Foto': datos[6], 'Descripcion': datos[7], 'Telefono': datos[8]}
            return user
        else:
            return None
    except Exception as ex: 
        raise ex

def read_user_bd_byMail(correo):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_User, Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono FROM users WHERE Correo = '{0}'".format(correo)
        cursor.execute(sql)
        datos = cursor.fetchone()

        if datos != None:
            user = {'ID_User': datos[0], 'Correo': datos[1],
                      'Username': datos[2], 'Nombre': datos[3],
                      'Contrasena': datos[4], 'FechaNac': datos[5],
                      'Foto': datos[6], 'Descripcion': datos[7], 'Telefono': datos[8]}
            return user
        else:
            return None
    except Exception as ex: 
        raise ex
    
def read_game_bd(id):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_Juego, Nombre, Descripcion, Imagen, Precio, Descuento, Genero, Plataforma, Clasificacion FROM games WHERE ID_Juego = {0}".format(id)
        cursor.execute(sql)
        datos = cursor.fetchone()

        if datos != None:
            game = {'ID_Juego': datos[0], 'Nombre': datos[1], 'Descripcion': datos[2],
                    'Imagen': datos[3], 'Precio': datos[4], 'Descuento': datos[5], 
                    'Genero': datos[6], 'Plataforma': datos[7], 'Clasificacion': datos[8]}
            return game
        else:
            return None
    except Exception as ex: 
        raise ex
    
def read_personal_data_bd(id_user):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_Data, ID_User, Tipo, NumeroTarjeta, Vigencia, CVC, NombrePropietario, ApellidoPropietario, Pais, CP FROM personal_data WHERE ID_User = {}".format(id_user)
        cursor.execute(sql)
        data = cursor.fetchone()

        if data != None:
            personal_data = {'ID_Data': data[0], 'ID_User': data[1], 'Tipo': data[2],
                             'NumeroTarjeta': data[3], 'Vigencia': data[4], 'CVC': data[5],
                             'NombrePropietario': data[6], 'ApellidoPropietario':data[7], 'Pais': data[8],
                             'CP': data[9]}
            return personal_data
        else:
            return None
    except Exception as ex:
        raise ex

def pagina_no_encontrada(error):
    return "<h1>La página que intentas buscar no existe</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()