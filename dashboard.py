from fastapi import FastAPI, Query, Request, HTTPException, Form, Depends, UploadFile, File,APIRouter
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import mysql.connector
from mysql.connector import Error
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from datetime import datetime
from fastapi.responses import HTMLResponse
from typing import Optional, List
import os
import shutil
import bcrypt


app = FastAPI()
router = APIRouter()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
labor="labor1"
respaldo="labor1_respaldo"
cedula_usuario = None

# Conexión a la base de datos
def get_mysql_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='init'
    )

# Modelo de datos para la información de la empresa
#modelo registro
class Datos_Empresa_registro(BaseModel):
    id: int
    nombre: str 
    correo: str 
    direccion: str
    numero: str
    nombre_emergencia: str
    numero_emergencia: str
    cargo: str
    password: str 

#modelo horario
class Horario(BaseModel):
    cedula: int
    reporte: str

class UpdatePassword(BaseModel):
    password: str
    new_password: str

#modelo hora extra
class Hora_extra(BaseModel):
    cedula: int
    reporte: str
    cantidad: int
    motivo: str

#modelo de reporte hora extra 
class Hora_extra_reporte(BaseModel):
    id: Optional[int] = None
    cedula: int
    nombre: Optional[str] = None
    reporte: str
    fecha: Optional[str] = None
    cantidad: int
    motivo: str

#modelo de reporte de horario
class Horario_reporte(BaseModel):
    id: Optional[int] = None
    cedula: Optional[int]
    nombre: Optional[str] = None
    reporte: Optional[str]
    fecha: str
    hora: Optional[str] = None

#modelo reporte de usuarios
class Datos_Empresa_usuarios(BaseModel):
    id: Optional[int] = None
    nombre: str
    correo: str
    direccion: str
    numero: str
    nombre_emergencia: str
    numero_emergencia: str
    cargo:str

#login
class Datos_Empresa_login(BaseModel):
    id: int
    nombre: str 
    correo: str 
    direccion: str
    numero: int
    password: str 

# Modelo de tarea
class Tarea(BaseModel):
    titulo: str
    descripcion: str
    completado: bool

class Tarea(BaseModel):
    titulo: str
    descripcion: str
    completado: bool

def obtener_nombre_usuario(cedula_usuario: int) -> str:
    nombre_usuario = None
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM datos_empresa WHERE id = %s", (cedula_usuario,))
        result = cursor.fetchone()
        if result:
            nombre_usuario = result[0]
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    return nombre_usuario



# Conexión a la base de datos
def get_mysql_connection():
    return mysql.connector.connect(
        host='localhost',
        port=3306,
        user='root',
        password='',
        database='init'
    )
#encriptar contraseñas
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

  
def obtener_usuarios_por_labor(labor: str) -> list:
    global usuarios
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM datos_empresa WHERE cargo = %s", (labor,))
        results = cursor.fetchall()
        usuarios = [row[0] for row in results]  # Extraer solo los nombres de usuario de los resultados
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    return usuarios

# validar permisos__________________________________________________________________________
def verificar_permiso_usuario():
    global cedula_usuario
    if cedula_usuario:
        try:
            conexion = get_mysql_connection()
            cursor = conexion.cursor()
            cursor.execute("SELECT cargo FROM datos_empresa WHERE id = %s", (cedula_usuario,))
            result = cursor.fetchone()
            if result:
                cargo = result[0]
                # Asigna un número específico para cada cargo
                if cargo == 'admin':
                    return 2
                else:
                    return 1
                # Agrega más condiciones para otros cargos si es necesario
        except Error as e:
            raise HTTPException(status_code=500, detail=str(e))
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

    return 0
# validar permisos__________________________________________________________________________

# Este endpoint imprime el valor de cedula_usuario_____________________________________________________________________________________________
# @app.get("/get_cedula_usuario")
# def get_cedula_usuario():
#     global cedula_usuario
#     try:
#         conexion = get_mysql_connection()
#         cursor = conexion.cursor()
#         cursor.execute("SELECT cargo FROM datos_empresa WHERE id = %s", (cedula_usuario,))
#         result = cursor.fetchone()
#         if result:
#             cargo = result[0]
#             return cargo
#         else:
#             return HTTPException(status_code=404, detail="Cargo no encontrado")
#     except Error as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     finally:
#         if conexion.is_connected():
#             cursor.close()
#             conexion.close()
# Este endpoint imprime el valor de cedula_usuario_____________________________________________________________________________________________
            


# def verificar_cargo(cedula_usuario):
#      cargo_usuario = None
#      try:
#          conexion = get_mysql_connection()
#          cursor = conexion.cursor()
#          cursor.execute("SELECT cargo FROM datos_empresa WHERE id = %s", (cedula_usuario,))
#          result = cursor.fetchone()
#          if result:
#              cargo_usuario = result[0]
#      except Error as e:
#          raise HTTPException(status_code=500, detail=str(e))
#      finally:
#          if conexion.is_connected():
#              cursor.close()
#              conexion.close()
#      return cargo_usuario
 
#______________________________________________________________________________________________________________________________

def obtener_cargo_usuario(request: Request) -> str:
    cargo_usuario = None
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT cargo FROM datos_empresa WHERE id = %s", (cedula_usuario,))
        result = cursor.fetchone()
        if result:
            cargo_usuario = result[0]
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    return cargo_usuario

def obtener_nombre_usuario(request: Request) -> str:
    nombre_usuario = None
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT nombre FROM datos_empresa WHERE id = %s", (cedula_usuario,))
        result = cursor.fetchone()
        if result:
            nombre_usuario = result[0]
    except Error as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
    return nombre_usuario
#______________________________________________________________________________________________________________________

#main____________________________________________________________________________________________________________________________  
base_url = "http://localhost:8000"

@app.get("/", tags=['home'])
async def message(request: Request):
    return templates.TemplateResponse("ingreso.html", {"request": request})

@app.get("/dashboard")
async def dashboard(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 1:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("dashboard_usuarios.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    elif permiso == 2:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("dashboard.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return templates.TemplateResponse("ingreso.html", {"request": request})


    
#main de admin___________________________________________________________________________________________________________________________
@app.get("/reporte-horarios")
def reporte_horarios(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("reportes_horario.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/registro-horarios")
def reporte_horarios(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("horarios.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/registro-horas-extras",)
def registro_horas_extras(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("reportes_horaextra.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")
        

@app.get("/usuarios")
def usuarios(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("usuarios.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/registro-usuarios")
def registro_usuarios(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:    
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("registro.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/labores", tags=['home'], response_class=HTMLResponse)
async def message(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:    
        try:
            conexion = get_mysql_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM {}".format(labor))
            datos = cursor.fetchall()
            nombre_usuario = obtener_nombre_usuario(request)
            cargo_usuario = obtener_cargo_usuario(request)
            return templates.TemplateResponse("asignarlabor.html", {"request": request, "datos": datos, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
        except mysql.connector.Error as ex:
            print("Error al obtener todos los datos:", ex)
            raise HTTPException(status_code=500, detail="Error al obtener todos los datos de la base de datos")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        return RedirectResponse(url="/")
    
@app.get("/filtros", tags=['home'], response_class=HTMLResponse)
async def message(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:
        try:
            conexion = get_mysql_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM {}".format(labor))
            datos = cursor.fetchall()
            nombre_usuario = obtener_nombre_usuario(request)
            cargo_usuario = obtener_cargo_usuario(request)
            return templates.TemplateResponse("filtros.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario, "datos": datos})
        except mysql.connector.Error as ex:
            print("Error al obtener todos los datos:", ex)
            raise HTTPException(status_code=500, detail="Error al obtener todos los datos de la base de datos")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        return RedirectResponse(url="/")


@app.get("/cambio_contraseña")
def registro_usuarios(request: Request,permiso: int = Depends(verificar_permiso_usuario)):

    if permiso == 2:    
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("actualizarpassword.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/actualizarimg") 
def registro_usuarios(request: Request,permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 2:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("cargarimg.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

#___________________________________________________________________________________________________________________________________
            

            
#MAIN USUARIOS_____________________________________________________________________________________________________________________
@app.get("/labores_usuarios")
async def dashboard(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 1:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("labor1.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/registro-horarios-usuarios")
def reporte_horarios(request: Request, permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 1:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("horariosusers.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})
    else:
        return RedirectResponse(url="/")

@app.get("/mensajes", tags=['home'])
async def message(request: Request):
    cargo_usuario = obtener_cargo_usuario(request)
    nombre_usuario = obtener_nombre_usuario(request)
    x = obtener_usuarios_por_labor(labor)
    usuarios = ', '.join(x)
    return templates.TemplateResponse("creartarea.html", {"request": request, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario, "usuarios": usuarios})

@app.get("/cambio_contraseña-usuarios")
def registro_usuarios(request: Request, permiso: int = Depends(verificar_permiso_usuario)):

    if permiso == 1:
        nombre_usuario = obtener_nombre_usuario(request)
        cargo_usuario = obtener_cargo_usuario(request)
        return templates.TemplateResponse("actualizarpassworduser.html", {"request": request, "cedula_usuario": cedula_usuario, "cargo_usuario": cargo_usuario, "nombre_usuario": nombre_usuario})   
    else:
        return RedirectResponse(url="/")
#MAIN USUARIOS_____________________________________________________________________________________________________________________
    


@app.get("/redireccionar")
def redireccionar(destino: str):
    endpoints = {
        "dashboard": "/dashboard",
        "reporte-horarios": "/reporte-horarios",
        "registro-horarios": "/registro-horarios",
        "registro-horas-extras": "/registro-horas-extras",
        "usuarios": "/usuarios",
        "registro-usuarios": "/registro-usuarios",
        "labores": "/labores",
        "filtros": "/filtros",
        "labores_usaurios": "/labores_usuarios"
    }
    if destino in endpoints:
        return RedirectResponse(url=endpoints[destino])
    else:
        raise HTTPException(status_code=404, detail="Endpoint no encontrado")
#main____________________________________________________________________________________________________________________________   

    

#login_________________________________________________________________________________________________________________________

@app.get("/user/", tags=['id'], status_code=200, response_model=Datos_Empresa_login)
def get_user(id: int, password: str):
    global cedula_usuario
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT password FROM datos_empresa WHERE id = %s", (id,))
        hashed_password = cursor.fetchone()
        
        if hashed_password:
            # Verificar si la contraseña ingresada coincide con la contraseña encriptada almacenada en la base de datos
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password[0].encode('utf-8')):
                # Contraseña válida, establecer el usuario como autenticado
                cedula_usuario = id
                return JSONResponse(content={"message": "Inicio de sesión exitoso"}, status_code=200)
            else:
                return JSONResponse(content={"message": "Contraseña incorrecta"}, status_code=401)
        else:
            return JSONResponse(content={"message": "Usuario no encontrado"}, status_code=404)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
#login_________________________________________________________________________________________________________________________


#registro____________________________________________________________________________________________________________________________________________
@app.post("/usuario", tags=['usuario'], response_model=None, status_code=201)
def create_usuario(usuario: Datos_Empresa_registro) -> dict:
    try:
        # Encriptar la contraseña antes de guardarla en la base de datos
        hashed_password = hash_password(usuario.password)
        
        # Establecer conexión con MySQL
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        
        # Insertar los datos en la tabla correspondiente, utilizando la contraseña encriptada
        cursor.execute(
            "INSERT INTO datos_empresa (id, nombre, correo, direccion, numero, nombre_emergencia, numero_emergencia, cargo, password) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)",
            (usuario.id, usuario.nombre, usuario.correo, usuario.direccion, usuario.numero, usuario.nombre_emergencia, usuario.numero_emergencia, usuario.cargo, hashed_password)
        )
        
        # Confirmar la inserción
        conexion.commit()
        
        return JSONResponse(content={"message": "Usuario creado exitosamente"}, status_code=201)
    
    except mysql.connector.Error as e:
        # Manejar errores de MySQL
        raise HTTPException(status_code=500, detail=f"Error en MySQL: {e}")
    
    finally:
        # Cerrar la conexión con MySQL
        if conexion.is_connected():
            cursor.close()
            conexion.close()
#registro____________________________________________________________________________________________________________________________________________
            



#horario______________________________________________________________________________________________________________
@app.post("/Horario", tags=['Horario'], response_model=None, status_code=201)
def create_horario(horario: Horario) -> JSONResponse:
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        
        # Obtener el nombre del empleado utilizando la cédula
        cursor.execute("SELECT nombre FROM datos_empresa WHERE id = %s", (horario.cedula,))
        nombre_empleado = cursor.fetchone()
        if not nombre_empleado:
            return JSONResponse(status_code=404, content={"message": f"No se encontró empleado para la cédula {horario.cedula}"})
        
        # Obtener la fecha y hora actual
        fecha_hora_actual = datetime.now()
        
        # Formatear la fecha y hora en el formato deseado
        fecha = fecha_hora_actual.strftime("%Y-%m-%d")
        hora = fecha_hora_actual.strftime("%H:%M:%S")
        
        # Insertar el nuevo horario en la base de datos
        cursor.execute("INSERT INTO horario (cedula, nombre, reporte, fecha, hora) VALUES (%s, %s, %s, %s, %s)", (horario.cedula, nombre_empleado[0], horario.reporte, fecha, hora))
        conexion.commit()
        return JSONResponse(content={"message": "Horario creado exitosamente"}, status_code=201)
    except Error as e:
        return JSONResponse(status_code=500, content={"message": f"Error al guardar el horario: {str(e)}"})
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
#hora extra
@app.post("/Hora_extra", tags=['Hora_extra'], response_model=None, status_code=201)
async def create_hora(hora: Hora_extra):
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        
        # Obtener el nombre del empleado utilizando la cédula
        cursor.execute("SELECT nombre FROM datos_empresa WHERE id = %s", (hora.cedula,))
        nombre_empleado = cursor.fetchone()
        if not nombre_empleado:
            raise HTTPException(status_code=404, detail=f"No se encontró empleado para la cédula {hora.cedula}")
        
        # Obtener la fecha y hora actual
        fecha_hora_actual = datetime.now()
        
        # Formatear la fecha en el formato deseado
        fecha = fecha_hora_actual.strftime("%Y-%m-%d")
        
        # Insertar la nueva hora extra en la base de datos
        cursor.execute("INSERT INTO hora_extra (cedula, nombre, reporte, fecha, cantidad, motivo) VALUES (%s, %s, %s, %s, %s, %s)", (hora.cedula, nombre_empleado[0], hora.reporte, fecha, hora.cantidad, hora.motivo))
        conexion.commit()
        return {"message": "Hora registrada exitosamente"}
    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Error al guardar la hora extra: {str(e)}")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
#horario______________________________________________________________________________________________________________
            




#reporte hora extra_______________________________________________________________________________________________________
@app.get("/Hora/", tags=['Hora'], status_code=200, response_model=List[Hora_extra_reporte])
@app.post("/Hora/", tags=['Hora'], status_code=200, response_model=List[Hora_extra_reporte])
def get_horas_por_rango_fechas(fecha_inicio: str = Query(..., alias="fecha_inicio"),
                                fecha_fin: str = Query(..., alias="fecha_fin")) -> List[Hora_extra_reporte]:
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # Convertir las cadenas de fecha en objetos datetime
        fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
        fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de fecha incorrecto. Utiliza el formato YYYY-MM-DD")

    if fecha_inicio_dt > fecha_fin_dt:
        raise HTTPException(status_code=400, detail="La fecha de inicio no puede ser posterior a la fecha de fin")

    try:
        # Realizar la consulta en la base de datos MySQL filtrando por el rango de fechas
        cursor.execute("SELECT * FROM hora_extra WHERE fecha BETWEEN %s AND %s", (fecha_inicio, fecha_fin))
        resultados = cursor.fetchall()

        horas_extra = []
        for fila in resultados:
            hora_extra = Hora_extra_reporte(**fila)
            horas_extra.append(hora_extra)
        
        return horas_extra
    
    except Error as ex:
        raise HTTPException(status_code=500, detail=f"Error al obtener las horas extra: {ex}")
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()
#reporte hora extra_______________________________________________________________________________________________________




#reporte horario_________________________________________________________________________________________________________________
@app.get("/Horario/", tags=['Horario'], status_code=200, response_model=List[Horario_reporte])
@app.post("/Horario/", tags=['Horario'], status_code=200, response_model=List[Horario_reporte])
def get_horario(fecha: str = Query(..., alias="fecha")) -> List[Horario_reporte]:
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor(dictionary=True)
        
        cursor.execute("SELECT * FROM horario WHERE fecha = %s", (fecha,))
        resultados = cursor.fetchall()
        
        horarios = []
        for fila in resultados:
            horario = Horario_reporte(**fila)
            horarios.append(horario)
        
        return horarios
    
    except Error as ex:
        raise HTTPException(status_code=500, detail=f"Error al obtener los horarios: {ex}")
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()

@app.get("/usuarios/", tags=['usuarios'], response_model=List[Datos_Empresa_usuarios])
def get_all_users() -> List[Datos_Empresa_usuarios]:
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM datos_empresa")
        results = cursor.fetchall()
        print(results)
        usuarios = []
        for row in results:
            usuario = Datos_Empresa_usuarios(id=row[0], nombre=row[1], correo=row[2], direccion=row[3], numero=row[4], nombre_emergencia=row[5],numero_emergencia=row[6],cargo=row[7] )
            usuarios.append(usuario)
            print(usuarios)
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.delete("/user/{id}", tags=['user'], response_model=dict)
def delete_user(id: int) -> dict:
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("DELETE FROM datos_empresa WHERE id = %s", (id,))
        conexion.commit()
        return {"message": "Usuario eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.get("/delete_user", response_class=HTMLResponse)
async def delete_user_form(request: Request):
    return templates.TemplateResponse("delete_user.html", {"request": request})

#reporte horario_________________________________________________________________________________________________________________




#crear tareas_________________________________________________________________________________________________________  

@app.post("/cambiar_labor/")
async def cambiar_labor(request: Request, labor_select: str = Form(...)):
    global labor
    labor = labor_select
    print("Labor actual cambiada a:", labor)  # Agregamos esto para verificar en la consola
    return {"mensaje": f"Se cambió la labor actual a {labor}"}


#crear tareas           
@app.post("/crear_tarea/")
async def crear_tarea(titulo: str = Form(...), descripcion: str = Form(...), completado: bool = Form(...)):
    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        consulta = "INSERT INTO {} (titulo, descripcion, fecha, completado) VALUES (%s, %s, %s, %s)".format(labor)
        valores = (titulo, descripcion, fecha_actual, completado)
        cursor.execute(consulta, valores)
        conexion.commit()
        return {"mensaje": "Tarea creada exitosamente"}
    except mysql.connector.Error as ex:
        print("Error al crear tarea:", ex)
        raise HTTPException(status_code=500, detail="Error al crear tarea en la base de datos")
    finally:
        if conexion.is_connected():
            cursor.close() 
            conexion.close()

# Ruta para actualizar todas las tareas y cambiar completado a False
@app.put("/actualizar_tareas/")
async def actualizar_tareas():
    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        consulta = "UPDATE {} SET completado = 0, fecha = %s".format(labor)
        valores = (fecha_actual,)
        cursor.execute(consulta, valores)
        conexion.commit()
        return {"mensaje": "Todas las tareas actualizadas correctamente"}
    except mysql.connector.Error as ex:
        print("Error al actualizar tareas:", ex)
        raise HTTPException(status_code=500, detail="Error al actualizar tareas en la base de datos")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()

@app.delete("/eliminar_tarea/{tarea_id}/")
async def eliminar_tarea(tarea_id: int):
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        consulta = "DELETE FROM {} WHERE id = %s".format(labor)
        valores = (tarea_id,)
        cursor.execute(consulta, valores)
        conexion.commit()
        return {"mensaje": f"Tarea con ID {tarea_id} eliminada correctamente"}
    except mysql.connector.Error as ex:
        print("Error al eliminar tarea:", ex)
        raise HTTPException(status_code=500, detail="Error al eliminar tarea en la base de datos")
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()


#crear tareas_________________________________________________________________________________________________________ 





#filtros por fecha_________________________________________________________________________________________________________________________

@app.post("/cambiar_labor3/")
async def cambiar_labor(request: Request, labor_select: str = Form(...)):
    global labor
    labor = labor_select
    print("Labor actual cambiada a:", labor)  # Agregamos esto para verificar en la consola
    return {"mensaje": f"Se cambió la labor actual a {labor}"}

@app.get("/filtrar_por_fecha/", tags=['filtrar'], response_class=HTMLResponse)
async def filtrar_por_fecha(request: Request, fecha: str = Query(...)):
    try:
        conexion = get_mysql_connection()
        cursor = conexion.cursor(dictionary=True)
        
        # Consulta SQL para filtrar por fecha
        query = f"SELECT * FROM {labor} WHERE fecha LIKE '%{fecha}%'"
        cursor.execute(query)
        
        # Obtener los resultados de la consulta
        datos = cursor.fetchall()
        
        return templates.TemplateResponse("filtros.html", {"request": request, "datos": datos})
    
    except mysql.connector.Error as ex:
        print("Error al filtrar por fecha:", ex)
        raise HTTPException(status_code=500, detail="Error al filtrar por fecha en la base de datos")
    
    finally:
        if conexion.is_connected():
            cursor.close()
            conexion.close()
#filtros por fecha_________________________________________________________________________________________________________________________





#labores usuarios_____________________________________________________________________________________________________________________________________________________
@app.get("/tareas_pendientes/")
def obtener_tareas_pendientes(cargo: str = Depends(obtener_cargo_usuario), permiso: int = Depends(verificar_permiso_usuario)):
    # Verificar si el usuario tiene permiso
    if permiso == 1:
        try:
            conexion = get_mysql_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM {} WHERE completado = 0".format(cargo))
            tareas_pendientes = cursor.fetchall()
            return tareas_pendientes 
        except mysql.connector.Error as ex:
            print("Error al obtener tareas pendientes:", ex)
            raise HTTPException(status_code=500, detail="Error al obtener tareas pendientes de la base de datos")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a estas tareas pendientes")

@app.get("/tareas_realizadas/")
def obtener_tareas_realizadas(cargo: str = Depends(obtener_cargo_usuario), permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 1:
        try:
            conexion = get_mysql_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM {} WHERE completado = 1".format(cargo))
            tareas_realizadas = cursor.fetchall()
            return tareas_realizadas
        except mysql.connector.Error as ex:
            print("Error al obtener tareas realizadas:", ex)
            raise HTTPException(status_code=500, detail="Error al obtener tareas realizadas de la base de datos")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a estas tareas realizadas")

# Marcar una tarea como completada y guardar en la base de datos de respaldo
@app.put("/completar_tarea/{tarea_id}/")
def completar_tarea(tarea_id: int, cargo: str = Depends(obtener_cargo_usuario ), permiso: int = Depends(verificar_permiso_usuario)):
    if permiso == 1:
        try:
            # Conectar a la base de datos
            conexion = get_mysql_connection()
            cursor = conexion.cursor()

            # Marcar la tarea como completada en la base de datos principal
            consulta_principal = "UPDATE {} SET completado = 1 WHERE id = %s".format(cargo)
            cursor.execute(consulta_principal, (tarea_id,))
            conexion.commit()

            # Obtener los detalles de la tarea completada
            cursor.execute("SELECT * FROM {} WHERE id = %s".format(cargo), (tarea_id,))
            tarea_completada = cursor.fetchone()

            # Obtener la hora actual en el momento de completar la tarea
            fecha_completado = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Obtener el nombre de la tabla de respaldo adecuada
            tabla_respaldo = cargo + "_respaldo"

            # Guardar los detalles de la tarea completada en la tabla de respaldo adecuada
            consulta_respaldo = "INSERT INTO {} (titulo, descripcion, fecha, completado) VALUES (%s, %s, %s, %s)".format(tabla_respaldo)
            valores_respaldo = (tarea_completada[1], tarea_completada[2], fecha_completado, tarea_completada[4])
            cursor.execute(consulta_respaldo, valores_respaldo)
            conexion.commit()

            return {"mensaje": "Tarea marcada como completada y guardada en la base de datos de respaldo"}
        except mysql.connector.Error as ex:
            print("Error al completar tarea:", ex)
            raise HTTPException(status_code=500, detail="Error al completar tarea en la base de datos")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()

@app.get("/todos/{cargo}")
def obtener_tareas_por_cargo(cargo: str, permiso: int = Depends(verificar_permiso_usuario)):
    # Verificar si el usuario tiene permiso
    if permiso == 1:
        try:
            conexion = get_mysql_connection()
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("SELECT * FROM init WHERE {} = 1".format(cargo))
            tareas_por_cargo = cursor.fetchall()
            return tareas_por_cargo
        except mysql.connector.Error as ex:
            print("Error al obtener tareas por cargo:", ex)
            raise HTTPException(status_code=500, detail="Error al obtener tareas por cargo de la base de datos")
        finally:
            if conexion.is_connected():
                cursor.close()
                conexion.close()
    else:
        raise HTTPException(status_code=403, detail="No tienes permiso para acceder a estas tareas por cargo")


#labores usuarios_____________________________________________________________________________________________________________________________________________________


#ACTUALIZAR CONTRASEÑA_________________________________________________________________________________________________________________________________________________

@app.put("/user/update_password/", tags=['user'], response_model=dict, status_code=200)
def update_password(passwords: UpdatePassword) -> dict:
    global cedula_usuario
    try:
        # Encriptar la nueva contraseña antes de actualizarla
        hashed_new_password = hash_password(passwords.new_password)
        
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT password FROM datos_empresa WHERE id = %s", (cedula_usuario,))
        result = cursor.fetchone()
        
        # Verificar si se encontró el usuario
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verificar si la contraseña actual coincide con la almacenada en la base de datos
        if verify_password(passwords.password, result[0]):
            # Actualizar la contraseña en la base de datos MySQL con la nueva contraseña encriptada
            cursor.execute("UPDATE datos_empresa SET password = %s WHERE id = %s", (hashed_new_password, cedula_usuario))
            conexion.commit()
            
            return {"message": "User password updated successfully"}
        else:
            raise HTTPException(status_code=401, detail="Incorrect current password")
    
    except mysql.connector.Error as ex:
        raise HTTPException(status_code=500, detail=f"Error during database operation: {ex}")
    
    finally:
        if 'conexion' in locals() and conexion.is_connected():
            cursor.close()
            conexion.close()






#_______________________________________Cargar imagenes_______________________________________________________________
            
@app.post("/upload-empleado")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Carpeta donde se guardarán las imágenes
        upload_folder = "static/img"
        # Nombre de archivo estándar
        filename = "empleado-del-mes.png"
        # Ruta completa del archivo
        file_path = os.path.join(upload_folder, filename)
        # Guardar la imagen en el servidor con el nombre estándar
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return {"message": "Image uploaded successfully", "file_path": file_path}
    except Exception as e:
        return {"message": f"Error uploading image: {str(e)}"}
    
@app.post("/upload-aseo")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Carpeta donde se guardarán las imágenes
        upload_folder = "static/img"
        # Nombre de archivo estándar
        filename = "lista-aseo.png"
        # Ruta completa del archivo
        file_path = os.path.join(upload_folder, filename)
        # Guardar la imagen en el servidor con el nombre estándar
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return {"message": "Image uploaded successfully", "file_path": file_path}
    except Exception as e:
        return {"message": f"Error uploading image: {str(e)}"}
    
@app.post("/upload-dashboard")
async def upload_image(image: UploadFile = File(...)):
    try:
        # Carpeta donde se guardarán las imágenes
        upload_folder = "static/img"
        # Nombre de archivo estándar
        filename = "dashboard.png"
        # Ruta completa del archivo
        file_path = os.path.join(upload_folder, filename)
        # Guardar la imagen en el servidor con el nombre estándar
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        return {"message": "Image uploaded successfully", "file_path": file_path}
    except Exception as e:
        return {"message": f"Error uploading image: {str(e)}"}
#_______________________________________Cargar imagenes_______________________________________________________________
    



#cambiar de labor 
@app.post("/cambiar_labor2/")
async def cambiar_labor(request: Request, labor_select: str = Form(...)):
    global labor
    labor = labor_select
    obtener_usuarios_por_labor(labor)
    print("Labor actual cambiada a:", labor)
    print(usuarios)  # Agregamos esto para verificar en la consola
    return {"mensaje": f"Se cambió la labor actual a {labor}"}

#crear tareas           
@app.post("/crear_tarea2/")
async def crear_tarea(titulo: str = Form(...), descripcion: str = Form(...)):
    try:
        fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conexion = get_mysql_connection()
        cursor = conexion.cursor()
        consulta = "INSERT INTO {} (titulo, descripcion, fecha, completado) VALUES (%s, %s, %s, %s)".format(labor)
        valores = (titulo, descripcion, fecha_actual, False)  # completado siempre se establece en False al crear una nueva tarea
        cursor.execute(consulta, valores)
        conexion.commit()
        return {"mensaje": "Tarea creada exitosamente"}
    except mysql.connector.Error as ex:
        print("Error al crear tarea:", ex)
        raise HTTPException(status_code=500, detail="Error al crear tarea en la base de datos")
    finally:
        if conexion.is_connected():
            cursor.close() 
            conexion.close()