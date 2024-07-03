from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout,login as auth_login
from django.utils import timezone
from . import models
'''
from django.views.generic import ListView, CreateView, DeleteView
from django.urls import reverse_lazy
'''
from django.views import View
import re
import uuid
import os
from . import models
from cliente import models as client_models
from django.core.files.storage import FileSystemStorage
from huerto import settings as st_py
from cliente import correo as send_correo

import io
from django.http import FileResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
# Create your views here.


def validar_username(username):
    users=User.objects.filter(username=username)
    if(users.exists()):
        return False
    else:
        return True
def validar_email(email):
    users=User.objects.filter(email=email)
    if(users.exists()):
        return False
    else:
        return True
def validar_password(password1,password2):
    if("" in [password1,password2]):
        return "Todos los campos son obligatorios"
    if(password1!=password2):
        return "Las contraseñas no coinciden"
    if not re.match(r'^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*\W).{8,}$', password1):
        return "La contraseña debe tener al menos 8 caracteres, incluyendo números, letras mayúsculas y minúsculas, y caracteres especiales."
    return "OK"   



def Solo_Letras_espacio(string):
    # Expresión regular para verificar que el string solo contiene letras y espacios
    patron = re.compile(r'^[a-zA-Z ]+$')
    return bool(patron.match(string))


def Solo_letras_numeros(string):
    # Expresión regular para verificar que el string solo contiene letras y números
    patron = re.compile(r'^[a-zA-Z0-9]+$')
    return bool(patron.match(string))

def formato_correo(correo):
    # Expresión regular para verificar el formato de un correo electrónico
    patron = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    return bool(patron.match(correo))

def validar_numero_cubano(numero):
    # Patrón para un número de teléfono cubano (ejemplo: +53 5 1234567)
    patron = r"^\+53\s[1-9]\d{8}$"
    if re.match(patron, numero):
        return True
    else:
        return False


def eliminar_imagen_producto(producto):
    # Obtener la URL de la imagen del objeto Producto
    url_imagen = producto.urlimagen
    
    # Construir la ruta completa del archivo en el servidor
    ruta_imagen=f"{st_py.BASE_DIR}\\{url_imagen[1:]}"
    ruta_imagen=ruta_imagen.replace('/','\\')
    print(ruta_imagen)
    # Verificar si el archivo existe y eliminarlo
    if os.path.isfile(ruta_imagen):
        os.remove(ruta_imagen)
        return True
    else:
        return False



def get_usuario(userid):
    try:
        return models.Usuario.objects.get(userid=userid)
    except Exception:
        return None
    
    
def cerrarsesion(request):
    logout(request)
    return redirect("../../../../../admin/")





class Login(View):
    def get(self,request):
        if(not request.user.is_authenticated):
            return render(request,"login/loguin.html")
        else:
            ## VER QUE TIPO DE USUARIO ES Y RETORNAR A ALGUN LADO ESPECIFICO
            if request.user.is_staff:
                return redirect("../../../admin/home/")
            else:
                u=get_usuario(request.user)
                if u.tipo=="Cliente":
                    return redirect("../../../../../../")
                elif u.tipo=="Dependiente":
                    return redirect("../../../../../../../dependiente/home/")
    

    def post(self,request):
        if(not request.user.is_authenticated):        
            username=request.POST.get("username")
            password=request.POST.get("password")
            back={"username":username,"password":password}
            user=User.objects.filter(username=username)
            if(user.exists()):
                user=user.first()
                if(user.check_password(password)):
                    user = authenticate(request,username=user.username, password=password)
                    if user is not None:
                        auth_login(request,user)
                        return redirect("../../../admin/")
            return render(request,"login/loguin.html",{"Alerta":"Nombre de usuario o contraseña incorrecto","back":back})        
        else:
            ## VER QUE TIPO DE USUARIO ES Y RETORNAR A ALGUN LADO ESPECIFICO
            if request.user.is_staff:
                return redirect("../../../admin/home/")
            else:
                u=get_usuario(request.user)
                if u.tipo=="Cliente":
                    return redirect("../../../../../../")
                elif u.tipo=="Dependiente":
                    return redirect("../../../../")


class Index(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"admin/home.html")
        else:
            return redirect("../../../../admin/")
        

class Gestionar_Mercancias(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"admin/gestion_Mercancia/index.html",{
                "productos":list(models.Producto.objects.all())
            })
        else:
            return redirect("../../../../admin/")
        

    def post(self,request):
        if request.user.is_authenticated:
            busqueda=str(request.POST.get("busqueda")).strip().lower()
            p=list(models.Producto.objects.all())
            productos=[]
            for pp in p:
                if busqueda in str(pp.nombre).lower():
                    productos.append(pp)
            return render(request,"admin/gestion_Mercancia/index.html",{
                "productos":productos
            })
        else:
            return redirect("../../../../admin/")
class Modificar_Producto(View):
    def get(self,request,productoid):
        if request.user.is_authenticated:
            producto=None
            try:
                producto=models.Producto.objects.get(id=productoid)
                return render(request,"admin/gestion_Mercancia/modificar/modificar_producto.html",{
                    "producto":producto
                })
            except Exception as e:
                return redirect("../../../../admin/mercancias/")
        else:
            return redirect("../../../../../../admin/")    


    def post(self,request,productoid):
        if request.user.is_authenticated:
            producto=None
            try:
                producto=models.Producto.objects.get(id=productoid)
                nombre=str(request.POST.get("nombre")).strip().capitalize()
                tipo=str(request.POST.get("categoria")).strip().capitalize()
                cantidad=str(request.POST.get("cantidad")).strip()
                precio=str(request.POST.get("precio"))
                imagen_producto = request.FILES.get('imagen_producto')
                if "" in [nombre,tipo,cantidad,precio]:
                    return render(request,"admin/gestion_Mercancia/modificar/modificar_producto.html",{
                        "producto":producto,"Alerta":"Todos los campos son obligatorios"
                    })
                
                # Validación de campos obligatorios
                if "" in [nombre, tipo, cantidad, precio] or not imagen_producto:
                    return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                        "Alerta": "Todos los campos son obligatorios",
                        "ret": request.POST
                    })
                
                # Validación de formato de campos
                if not re.match(r'^[a-zA-Z ]+$', nombre) or not re.match(r'^[a-zA-Z]+$', tipo):
                    return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                        "Alerta": "El nombre y el tipo deben contener solo letras",
                        "ret": request.POST
                    })
                if not cantidad.isdigit() or int(cantidad) < 0 or not precio.isdigit() or float(precio) <= 0:
                    return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                        "Alerta": "La cantidad y el precio deben ser números positivos",
                        "ret": request.POST
                    })


                if nombre!=producto.nombre or tipo!=producto.tipo:
                    if not models.Producto.objects.filter(nombre=nombre,tipo=tipo).exists():
                        producto.nombre=nombre
                        producto.tipo=tipo
                producto.cantidad=cantidad
                producto.precio=precio
                producto.ultimo_update=timezone.now()
                producto.save()
                if imagen_producto:
                    fs = FileSystemStorage()
                    filename = fs.save(imagen_producto.name, imagen_producto)
                    uploaded_file_url = fs.url(filename)    
                    eliminar_imagen_producto(producto=producto)
                    producto.urlimagen=uploaded_file_url
                    producto.save()
                return redirect("../../../../admin/mercancias/")
            except Exception as e:
                return redirect("../../../../admin/mercancias/")
        else:
            return redirect("../../../../../../admin/")    
class Agregar_Producto(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request, "admin/gestion_Mercancia/agregar/agregar.html")
        else:
            return redirect('../../../../../admin/')


    def post(self,request):  
        if request.user.is_authenticated:
            nombre = str(request.POST.get("nombre")).strip().capitalize()
            tipo = str(request.POST.get("categoria")).strip().capitalize()
            cantidad = str(request.POST.get("cantidad")).strip()
            precio = str(request.POST.get("precio")).strip()
            ret = {
                "nombre": nombre, "tipo": tipo, "cantidad": cantidad, "precio": precio
            }
            imagen_producto = request.FILES.get('imagen_producto')
            
            # Validación de campos obligatorios
            if "" in [nombre, tipo, cantidad, precio] or not imagen_producto:
                return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                    "Alerta": "Todos los campos son obligatorios",
                    "ret": ret
                })
            
            # Validación de formato de campos
            if not re.match(r'^[a-zA-Z ]+$', nombre) or not re.match(r'^[a-zA-Z]+$', tipo):
                return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                    "Alerta": "El nombre y el tipo deben contener solo letras",
                    "ret": ret
                })
            if not cantidad.isdigit() or int(cantidad) < 0 or not precio.isdigit() or float(precio) <= 0:
                return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                    "Alerta": "La cantidad y el precio deben ser números positivos",
                    "ret": ret
                })
            
            m = None
            if not models.Producto.objects.filter(nombre=nombre, tipo=tipo).exists():
                fs = FileSystemStorage()
                filename = fs.save(imagen_producto.name, imagen_producto)
                uploaded_file_url = fs.url(filename)
                try:
                    nuevo_producto = models.Producto(nombre=nombre, tipo=tipo, cantidad=cantidad, precio=precio, urlimagen=uploaded_file_url)
                    nuevo_producto.save()
                    m = "Producto Registrado correctamente"
                except Exception as e:
                    pass
            else:
                return render(request, "admin/gestion_Mercancia/agregar/agregar.html", {
                    "Alerta": "El producto ya existe",
                    "ret": ret
                })
            return redirect("../../../../../admin/mercancias/")
        else:
            return redirect("../../../../admin/")   
class Eliminar_Producto(View):
    def get(self,request,productoid):
        if request.user.is_authenticated:
            models.Producto.objects.get(id=productoid).delete()
            return redirect("../../../../../../admin/mercancias/")
        else:
            return redirect("../../../../admin/")
        


#### CRUD USUARIO ####

class Gestionar_Usuarios(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"admin/gestion_usuarios/gestion_usuarios.html",{
                'dependientes':list(models.Dependiente.objects.all())
            })
        else:
            return redirect("../../../../admin/")
        

    def post(self,request):
        if request.user.is_authenticated:
            usuario=str(request.POST.get("buscar")).lower().split()
            dependientes=[]
            dd=list(models.Dependiente.objects.all())
            for d in dd:
                if any(u in str(d.usuarioid.userid.username) for u in usuario):
                    dependientes.append(d)
            return render(request,"admin/gestion_usuarios/gestion_usuarios.html",{
                'dependientes':dependientes
            })
        else:
            return redirect("../../../../admin/")
class Agregar_Usuario(View):
    def get(self,request):
        if request.user.is_authenticated:
            if request.user.is_staff:
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html")
        return redirect("../../../../../admin/")
        
    def post(self,request):
        if request.user.is_authenticated:
            nombre=str(request.POST.get("nombre")).strip().title()
            apellidos=str(request.POST.get("apellidos")).strip().title()
            telefono=str(request.POST.get("telefono")).strip()
            username=str(request.POST.get('username')).strip().lower()
            email=str(request.POST.get('email')).strip()
            password1=request.POST.get('password1')
            password2=request.POST.get('password2')
            if "" in [username,email,password1,password2]:
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"Todos los campos son obligatorios",
                    "ret":request.POST
                })
            if User.objects.filter(username=username).exists():
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"Nombre de usuario en uso",
                    "ret":request.POST
                })
            if User.objects.filter(email=email).exists():
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"Correo electronico en uso",
                    "ret":request.POST
                })
            v=validar_password(password1=password1,password2=password2)
            if(v!="OK"):
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":v,
                    "ret":request.POST
                })
            
            if not Solo_Letras_espacio(nombre):
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"El nombre solo admite letras y el caracter espacio",
                    "ret":request.POST
                })
            
            if not Solo_Letras_espacio(apellidos):
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"El apellido solo admite letras y el caracter espacio",
                    "ret":request.POST
                })
            
            if not Solo_letras_numeros(username):
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"El nombre de usuario solo admite letras y numeros",
                    "ret":request.POST
                })
            
            if not formato_correo(email):
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"El correo electronico no tiene el formato correcto",
                    "ret":request.POST
                })
            
            if not validar_numero_cubano(telefono):
                return render(request,"admin/gestion_usuarios/agregar_usuario/agregar_usuario.html",{
                    "Alerta":"El numero de telfono no tiene el formato de numero movil cubano",
                    "ret":request.POST
                })
            
            nu=User(username=username,email=email)
            nu.set_password(password1)
            nu.save()
            nuu=models.Usuario(userid=nu,tipo="Dependiente")
            nuu.save()
            nd=models.Dependiente(usuarioid=nuu,nombre=nombre,apellidos=apellidos,telefono=telefono)
            nd.save()

            return redirect("../../../../../admin/gestion_usuarios/")
        else:
            return redirect("../../../../admin/")
class Eliminar_usuario(View):
    def get(self,request,empleadoid):
        if request.user.is_authenticated:
            try:
                du=models.Usuario.objects.get(id=empleadoid)
                du.userid.delete()
                du.delete()
                return redirect("../../../../admin/gestion_usuarios/")
            except Exception as e:
                return redirect("../../../../admin/gestion_usuarios/")
        else:
            return redirect("../../../../admin/")        






class Perfil(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"admin/perfil/perfil.html")
        else:
            return redirect("../../../../admin/")
    
    def post(self,request):
        if request.user.is_authenticated:
            try:
                password0=request.POST.get("password0")
                password1=request.POST.get("password1")
                password2=request.POST.get("password2")
                if "" in [password1,password0,password2]:
                    return render(request,"admin/perfil/perfil.html",{
                        "Alerta":"Todos los campos son obligatorios"
                    })
                if(request.user.check_password(password0)):
                    v=validar_password(password1=password1,password2=password2)
                    if v!="OK":
                        return render(request,"admin/perfil/perfil.html",{
                            "Alerta":v
                        })  
                    request.user.set_password(password1)
                    request.user.save()
                    user = authenticate(request,username=request.user.username, password=password1)
                    if user is not None:
                        auth_login(request,user)
                        return redirect("../../../../../../../../../../admin/")
                else:
                    return render(request,"admin/perfil/perfil.html",{
                        "Alerta":"Contraseña incorrecta"
                    })
            except Exception as e:
                print(e)
        return redirect("../../../../../admin/")



class Correo(View):
    def get(self,request):
        if request.user.is_authenticated:
            return render(request,"admin/correo/correo.html",{
                "correos":list(client_models.Comentario.objects.all().order_by('-id'))
            })
        else:
            return redirect("../../../../admin/")


class Responder_Comentario(View):
    def get(self,request,comentarioid):
        if request.user.is_authenticated:
            try:
                comentario=client_models.Comentario.objects.get(id=comentarioid)
                return render(request,"admin/correo/responder.html",{
                    "comentario":comentario
                })
            except Exception as e:
                print(e)
                return redirect("../../../../../../../../../../../../admin/correo/")
        else:
            return redirect("../../../../admin/")

    def post(self,request,comentarioid):
        if request.user.is_authenticated:
            try:
                comentario=client_models.Comentario.objects.get(id=comentarioid)
                print(comentario.email)
                asunto=str(request.POST.get("asunto")).strip()
                mensaje=str(request.POST.get("mensaje")).strip()
                if "" in [asunto,mensaje]:
                    return render(request,"admin/correo/responder.html",{
                        "comentario":comentario,"Alerta":"Todos los campos son obligatorios"
                    })
                send_correo.enviar_correo_con_asunto(s=mensaje,email=comentario.email,asunto=asunto)
                return redirect("../../../../../../../../../../../../admin/correo/")
            except Exception as e:
                print(e)
                return redirect("../../../../../../../../../../../../admin/correo/")
        else:
            return redirect("../../../../admin/")

class Eliminar_Comentario(View):
    def get(self,request,comentarioid):
        if request.user.is_authenticated:
            try:
                comentario=client_models.Comentario.objects.get(id=comentarioid)
                comentario.delete()
            except Exception as e:
                print(e)
            return redirect("../../../../../../../../../../../../admin/correo/")
        else:
            return redirect("../../../../admin/")




def exportar_inventario(request):
    if request.user.is_authenticated:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Obtén los datos de los productos desde la base de datos
        productos = models.Producto.objects.all()

        # Crea una lista de filas para la tabla
        rows = [["Nombre", "Tipo", "Cantidad", "Precio"]]

        for producto in productos:
            rows.append([producto.nombre, producto.tipo, producto.cantidad, producto.precio])

        # Crea la tabla con los datos
        table = Table(rows)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ]))

        # Agrega la tabla al documento
        doc.build([table])

        # Devuelve el PDF como una respuesta de archivo adjunto
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="inventario.pdf")
    else:
        return redirect("../../../../admin/")
    


def exportar_reporte(request):
    if request.user.is_authenticated:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)

        # Obtén los datos de los productos desde la base de datos
        productos_faltantes = models.Producto.objects.filter(cantidad=0)
        productos_sobrantes = models.Producto.objects.filter(cantidad__gt=500)

        # Crea una lista de filas para la tabla de productos faltantes
        rows_faltantes = [["Nombre", "Tipo", "Cantidad", "Precio"]]

        for producto in productos_faltantes:
            rows_faltantes.append([producto.nombre, producto.tipo, producto.cantidad, producto.precio])

        # Crea una lista de filas para la tabla de productos sobrantes
        rows_sobrantes = [["Nombre", "Tipo", "Cantidad", "Precio"]]

        for producto in productos_sobrantes:
            rows_sobrantes.append([producto.nombre, producto.tipo, producto.cantidad, producto.precio])

        # Crea las tablas con los datos
        table_faltantes = Table(rows_faltantes)
        table_sobrantes = Table(rows_sobrantes)

        # Establece estilos para las tablas
        table_style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
        ])

        table_faltantes.setStyle(table_style)
        table_sobrantes.setStyle(table_style)

        # Agrega etiquetas para describir las tablas
        styles = getSampleStyleSheet()
        etiqueta_faltantes = Paragraph("<b>Productos con cantidad igual a cero (Faltante)</b>", styles["Heading1"])
        etiqueta_sobrantes = Paragraph("<b>Productos con cantidad mayor que 500 (Sobrante)</b>", styles["Heading1"])

        # Agrega las tablas y etiquetas al documento
        flowables = [etiqueta_faltantes, table_faltantes, etiqueta_sobrantes, table_sobrantes]
        doc.build(flowables)

        # Devuelve el PDF como una respuesta de archivo adjunto
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="reporte.pdf")
    else:
        return redirect("../../../../admin/")
    

