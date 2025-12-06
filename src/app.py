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
#Añadir filtros!!!!!!
@app.route('/busqueda-de-amigos', methods=['POST'])
def search():
    try:
        cursor = conexion.connection.cursor()
        if request.json == None:
            sql = "SELECT ID_User, Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono FROM users"
        else:
            sql = """SELECT ID_User, Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono FROM users WHERE NOT ID_User = {0}""".format(request.json['ID_User'])
        cursor.execute(sql)
        data = cursor.fetchall()

        if request.json == None:
            users=[]
            for row in data:
                user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 0}
                users.append(user)
            return jsonify({'users': users, 'mensaje':"Usuarios encontrados", 'exito': True})
        else:
            users=[]
            for row in data:
                frienddata_sended = read_friend_bd(request.json['ID_User'], row[0])
                frienddata_received = read_friend_bd(row[0], request.json['ID_User'])

                if frienddata_sended is None:
                    frienddata_sended = {'Status': 0}

                if frienddata_received is None:
                    frienddata_received = {'Status': 0}

                if frienddata_sended['Status'] == 1:
                    user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 2}
                    users.append(user)
                    continue
                elif frienddata_sended['Status'] == 2:
                    user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 5}
                    users.append(user)
                    continue
                elif frienddata_sended['Status'] == 4:
                    user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 4}
                    users.append(user)
                    continue
                elif frienddata_received['Status'] == 1:
                    user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 3}
                    users.append(user)
                    continue
                elif frienddata_received['Status'] == 4:
                    user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 6}
                    users.append(user)
                    continue
                else:
                    user = {'ID_User': row[0], 'Correo': row[1],
                      'Username': row[2], 'Nombre': row[3],
                      'Contrasena': row[4], 'FechaNac': row[5],
                      'Foto': row[6], 'Descripcion': row[7], 'Telefono': row[8],
                      'Status': 1}
                    users.append(user)
                    continue
            return jsonify({'users': users, 'mensaje': 'Mostrando usuarios encontrados', 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar alumnos:{}"+str(ex), 'exito':False})

#mostrar usuario específico
@app.route('/perfil/<id>', methods=['POST'])
def perfil(id):
    try:
        user = read_user_bd(id, 0)
        if request.json == None:
            return jsonify({'user': user, 'mensaje':"Usuario encontrado", 'exito': True})
        else:
            frienddata_sended = read_friend_bd(request.json['ID_User'], id)
            frienddata_received = read_friend_bd(id, request.json['ID_User'])

            if frienddata_sended is None:
                frienddata_sended = {'Status': 0}

            if frienddata_received is None:
                frienddata_received = {'Status': 0}
            
            if frienddata_sended['Status'] == 1:
                user['Status'] = 2
            elif frienddata_sended['Status'] == 2:
                user['Status'] = 5
            elif frienddata_sended['Status'] == 4:
                user['Status'] = 4
            elif frienddata_received['Status'] == 1:
                user['Status'] = 3
            elif frienddata_received['Status'] == 4:
                user['Status'] = 6
            else:
                user['Status'] = 1
            
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
    
@app.route('/contrasena/<id>', methods=['PUT'])
def contrasenaUpdate(id):
    try:
        user = read_user_bd(id)
        if user != None:
            cursor = conexion.connection.cursor()
            sql = """UPDATE users SET Contrasena = '{0}' WHERE ID_User = {1}""".format(request.json['Contrasena'], id)
            cursor.execute(sql)
            conexion.connection.commit()
            return jsonify({'mensaje': "Contraseña actualizada", 'exito': True})
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

@app.route('/admin/reportes', methods=['POST'])
def adminViewReports():
    try:
        cursor = conexion.connection.cursor()
        if request.json == None:
            sql = """
            SELECT Correo, Tema, Descripcion, Imagen FROM reports"""
        else:
            sql = """
            SELECT Correo, Tema, Descripcion, Imagen FROM reports WHERE Tema = '{0}'""".format()
        
        cursor.execute(sql)
        data = cursor.fetchall()

        reports=[]
        for row in data:
            report = {'Correo': row[0], 'Tema': row[1],
                      'Descripcion': row[2], 'Imagen': row[3]}
            reports.append(sale)
        return jsonify({'reporst': reports, 'mensaje':"Usuarios encontrados", 'exito': True})

    except Exception as ex:
        return jsonify({'mensaje': "Error {0} ".format(ex), 'exito': False})

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
        return jsonify({'mensaje': "Peticion de recuperación registrada", 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

# ----- AUTENTICACIÓN ----- 

@app.route('/codigoveri', methods=['POST'])
def createAuthRequest():
    try:
        user = read_user_bd_byMail(request.json['Correo'])

        if user == None:
            return jsonify({'mensaje': "No se ha encontrado un usuario con ese correo", 'exito': False})

        cursor = conexion.connection.cursor()
        sql = """
            INSERT INTO auth 
            (ID_User, Code)
            VALUES (%s, %s)
        """

        valores = (
            user['ID_User'],
            randint(100000, 999999)
        )
        cursor.execute(sql, valores)
        conexion.connection.commit()
        deleteAfterDelay(cursor.lastrowid)
        return jsonify({'mensaje': "Peticion de recuperación registrada", 'exito': True})
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

@app.route('/correoveri', methods=['POST'])
def checkAuthCode():
    try:
        user = read_user_bd_byMail(request.json['Correo'])
        
        cursor = conexion.connection.cursor()
        
        sql = "SELECT Code FROM auth WHERE ID_User = {0}".format(user['ID_User'])
        cursor.execute(sql)
        data = cursor.fetchone()
        if data == None:
            return jsonify({'mensaje': "No se encontró registro", 'exito': False})
        if data[0] == request.json['Code']:
            return jsonify({'mensaje': "El usuario ha sido autenticado con éxito", 'exito': True})
        else:
            return jsonify({'mensaje': "Codigo incorrecto", 'exito': False})

    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

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
        sql = """INSERT INTO sales (ID_User, Fecha, ID_Juego, PrecioTotal, Descuento)
        VALUES (%s, %s, %s, %s, %s)"""
        valores = (
            request.json['ID_User'],
            request.json['Fecha'],
            request.json['ID_Juego'],
            request.json['PrecioTotal'],
            request.json['Descuento']
        )
        
        cursor.execute(sql, valores)
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
    
@app.route('/admin/ventas', methods=['GET'])
def adminViewSales():
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_Sale, ID_User, Fecha, ID_Juego, PrecioTotal, Descuento FROM sales"""
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

@app.route('/friends/<id>', methods=['GET'])
def viewFriendsList(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_User1, ID_User2, Status, Fecha FROM friends WHERE (ID_User1 = {0} OR ID_User2 = {0}) AND Status = 2""".format(id)
        cursor.execute(sql)
        data = cursor.fetchall()
        friends=[]
        for row in data:
            request = {'ID_User1': row[0], 'ID_User2': row[1], 'Status': row[2], 'Fecha': row[3]}
            friends.append(request)
        return jsonify({'friends': friends, 'mensaje': 'Mostrando solicitudes de amistad', 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar juegos: "+str(ex), 'exito': False})

@app.route('/friendrequests/<id>', methods=['GET'])
def viewFriendsRequestsList(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_User1, Status, Fecha FROM friends WHERE ID_User2 = {0} AND Status = 1""".format(id)
        cursor.execute(sql)
        data = cursor.fetchall()
        requests=[]
        for row in data:
            request = {'ID_User': row[0], 'Status': row[1], 'Fecha': row[2]}
            requests.append(request)
        return jsonify({'requests': requests, 'mensaje': 'Mostrando solicitudes de amistad', 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar juegos: "+str(ex), 'exito': False})

@app.route('/blocked/<id>', methods=['GET'])
def viewBlockedList(id):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_User2, Status, Fecha FROM friends WHERE ID_User1 = {0} AND Status = 4""".format(id)
        cursor.execute(sql)
        data = cursor.fetchall()
        requests=[]
        for row in data:
            request = {'ID_User': row[0], 'Status': row[1], 'Fecha': row[2]}
            requests.append(request)
        return jsonify({'requests': requests, 'mensaje': 'Mostrando solicitudes de amistad', 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error al listar juegos: "+str(ex), 'exito': False})

@app.route('/friendrequest', methods=['POST'])
def sendFriendRequest():
    try:
        status = update_friend_status(request.json['ID_User1'], request.json['ID_User2'], 1, request.json['Fecha'])
        return jsonify({'mensaje': "Actualizado con exito " + status.get_json()['mensaje'] , 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error "+str(ex), 'exito': False})

@app.route('/friends', methods=['POST'])
def acceptFriend():
    try:
        status = update_friend_status(request.json['ID_User1'], request.json['ID_User2'], 2, request.json['Fecha'])
        return jsonify({'mensaje': "Actualizado con exito "+ status.get_json()['mensaje'], 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error "+str(ex), 'exito': False})

@app.route('/blocked', methods=['POST'])
def block():
    try:
        status = update_friend_status(request.json['ID_User1'], request.json['ID_User2'], 4, request.json['Fecha'])
        return jsonify({'mensaje': "Actualizado con exito "+ status.get_json()['mensaje'], 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error "+str(ex), 'exito': False})

@app.route('/cancelrequest', methods=['POST'])
def cancelRequest():
    try:
        status = update_friend_status(request.json['ID_User1'], request.json['ID_User2'], 3, request.json['Fecha'])
        return jsonify({'mensaje': "Actualizado con exito "+ status.get_json()['mensaje'], 'exito': True})
    except Exception as ex:
        return jsonify({'mensaje': "Error "+str(ex), 'exito': False})

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
        return jsonify({'mensaje': "Error al listar juegos: "+str(ex), 'exito': False})

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
def read_user_bd(id, status = 0):
    try:
        cursor = conexion.connection.cursor()
        sql = "SELECT ID_User, Correo, Username, Nombre, Contrasena, FechaNac, Foto, Descripcion, Telefono FROM users WHERE ID_User = {0}".format(id)
        cursor.execute(sql)
        datos = cursor.fetchone()

        if datos != None:
            user = {'ID_User': datos[0], 'Correo': datos[1],
                      'Username': datos[2], 'Nombre': datos[3],
                      'Contrasena': datos[4], 'FechaNac': datos[5],
                      'Foto': datos[6], 'Descripcion': datos[7], 'Telefono': datos[8], 'Status': status}
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
        sql = "SELECT ID_Juego, Nombre, Descripcion, Imagen, Precio, Descuento, Genero, Plataforma, Clasificación FROM games WHERE ID_Juego = {0}".format(id)
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

def read_friend_bd(id_user1, id_user2):
    try:
        cursor = conexion.connection.cursor()
        sql = """SELECT ID_User1, ID_User2, Status, Fecha FROM friends WHERE ID_User1 = {0} AND ID_User2 = {1}""".format(id_user1, id_user2)
        cursor.execute(sql)
        data = cursor.fetchone()

        if data != None:
            friend_data = {'ID_User1': data[0], 'ID_User2': data[1], 'Status': data[2], 'Fecha': data[3]}
            return friend_data
        else:
            return None
    except Exception as ex:
        raise ex

def update_friend_status(id_user1, id_user2, status, fecha):
    try:
        if read_user_bd(id_user1) == None or read_user_bd(id_user2) == None:
            return jsonify({'mensaje': "No se ha encontrado uno de los usuarios", 'exito': False})
        
        friend_data = read_friend_bd(id_user1, id_user2)

        cursor = conexion.connection.cursor()
        
        if friend_data == None:
            sql = """INSERT INTO friends (ID_User1, ID_User2, Status, Fecha)
            values (%s, %s, %s, %s)"""

            valores = (
            id_user1,
            id_user2,
            status,
            fecha
            )
            cursor.execute(sql, valores)
            conexion.connection.commit()
            return jsonify({'mensaje': "Amigo registrado", 'exito': True})
        else:
            sql = """UPDATE friends SET Status = %s, Fecha = %s WHERE ID_User1 = %s AND ID_User2 = %s"""
            
            valores = (
                status,
                fecha,
                id_user1,
                id_user2
            )
            cursor.execute(sql, valores)
            conexion.connection.commit()
            return jsonify({'mensaje': 'Se ha actualizado la fila de amigos con éxito', 'exito': True})

    except Exception as ex:
        return jsonify({'mensaje': "Error {0}".format(ex), 'exito': False})

def pagina_no_encontrada(error):
    return "<h1>La página que intentas buscar no existe</h1>", 404

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.register_error_handler(404, pagina_no_encontrada)
    app.run()