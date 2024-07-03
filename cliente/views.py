from django.shortcuts import render,redirect
from django.views import View
from administrador import models as models_admin
from . import models
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, logout,login as auth_login
# Create your views here.

import re,uuid
from . import correo

def mensaje_validacion_email(username,tocken):
    return f'''
Estimado {username}:

Usted se ha registrado en la plataforma digital del huerto de la UCI.

Su codigo de verificacion es:

{tocken}


'''
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


def get_carrito(user):
    try:
        cliente=models.Cliente.objects.get(usuarioid=models_admin.Usuario.objects.get(userid=user))
        carrito=list(models.Carrito.objects.filter(clienteid=cliente))
        contexto=[]
        for cc in carrito:
            contexto.append({"carrito":cc,"subtotal":cc.productoid.precio*cc.cantidad})
        return contexto
    except Exception as e:
        print(e)
        return None
def tamanio_carrito(carrito):
    try:
        return carrito.__len__()
    except Exception as e:
        print(e)
        return None

def total_monto(carrito):
    try:
        total=0.0
        for cc in carrito:
            total+=cc.get("subtotal")
        return total
    except Exception as e:
        print(e)
        return None



def get_Compras(user):
    try:
        cliente=models.Cliente.objects.get(usuarioid=models_admin.Usuario.objects.get(userid=user))
        compras=list(models.Compra.objects.filter(clienteid=cliente).order_by('-id'))
        contexto=[]
        if compras.__len__() > 0:
            for cc in compras:
                detalles=list(models.Detalle.objects.filter(compraid=cc))
                dd=[]
                for d in detalles:
                    dd.append({"detalle":d,"subtotal":d.cantidad*d.productoid.precio})
                if dd.__len__()==0:
                    dd=None
                contexto.append({"compra":cc,"detalles":dd})
            if contexto.__len__()>0:
                return contexto
            return None
    except Exception as e:
        print(e)
    return None
########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


class Index(View):
    def get(self,request):
        carrito=get_carrito(request.user)
        return render(request,"cliente/demo1.html",{
            "productos":list(models_admin.Producto.objects.all()),
            "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito)
        })
    
    def post(self,request):
        carrito=get_carrito(request.user)
        productos=[]
        buscar=str(request.POST.get("buscar")).strip().lower()
        pr=list(models_admin.Producto.objects.all())
        for pp in pr:
            if buscar in str(pp.nombre).lower():
                productos.append(pp)
        return render(request,"cliente/busqueda.html",{
            "productos":productos,
            "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito)
        })
    
class Categoria(View):
    def get(self,request,categoria):
        productos=list(models_admin.Producto.objects.filter(tipo=categoria))
        carrito=get_carrito(request.user)
        return render(request,"cliente/busqueda.html",{
            "productos":productos,
            "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito)
        })



class Login(View):
    def post(self,request):
        if not request.user.is_authenticated:        
            email=str(request.POST.get("email")).strip()
            password=request.POST.get("password")
            user=User.objects.filter(email=email)
            if(user.exists()):
                user=user.first()
                if(user.check_password(password)):
                    user = authenticate(request,username=user.username, password=password)
                    if user is not None:
                        auth_login(request,user)
                    
                    usu=models_admin.Usuario.objects.get(userid=user)
                    try:
                        cliente=models.Cliente.objects.get(usuarioid=usu,verificado=False)
                        return redirect("../../../../../../../verificacion_correo/")
                    except Exception:
                        pass
                    return redirect("../../../../../../../")
            return render(request,"cliente/demo1.html",{
                "productos":list(models_admin.Producto.objects.all()),
                "Alerta":"Nombre de usuario o contraseña incorrecto",
                "back":request.POST
            })
        else:
            return redirect("../../../../../../../")


class Logout(View):
    def get(self, request):
        logout(request)
        return redirect("../../../../../../../")


class Verificacion(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                u=models_admin.Usuario.objects.get(userid=request.user)
                cliente=models.Cliente.objects.get(usuarioid=u)
                if cliente.verificado==False:
                    tocken=str(uuid.uuid4()).strip()
                    indice=tocken.find('-')
                    tocken=tocken[:indice]
                    cliente.tocken=tocken
                    cliente.save()
                    print(tocken)
                    correo.enviar_correo(mensaje_validacion_email(request.user.username,tocken),request.user.email)
                else:
                    return redirect("../../../../../../")
            except Exception:
                pass
            return render(request,"cliente/verificacion_correo.html")
        else:
            return redirect("../../../../../../../")

    def post(self,request):
        if request.user.is_authenticated:
            tocken=str(request.POST.get("tocken")).strip()
            try:
                usuario=models_admin.Usuario.objects.get(userid=request.user)
                cliente=models.Cliente.objects.get(usuarioid=usuario,verificado=False)
                m=None
                if cliente.tocken==tocken:
                    cliente.verificado=True
                    cliente.tocken=None
                    cliente.save()
                    return redirect("../../../../../../")
                else:   
                    return render(request,"cliente/verificacion_correo.html",{
                        "Alerta":"Lo siento, tocken incorrecto"
                    })
            except Exception:
                pass
        else:
            return redirect("../../../../../../../")


class Registro(View):
    def post(self,request):
        if not request.user.is_authenticated:
            username=str(request.POST.get("username")).strip().lower()
            email=str(request.POST.get("email")).strip()
            direccion=str(request.POST.get("direccion")).strip()
            password1=request.POST.get("password1")
            password2=request.POST.get("password2")
            print(request.POST)
            if "" in [username,email,direccion,password1,password2]:
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":"Todos los campos son obligatorios",
                    "back":request.POST
                })
            if not Solo_letras_numeros(username):
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":"El nombre de usuario solo admite letras y numeros",
                    "back":request.POST
                })
            if not formato_correo(email):
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":"El formato del correo es incorrecto",
                    "back":request.POST
                })
            if User.objects.filter(username=username).exists():
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":"Nombre de usuario en uso",
                    "back":request.POST
                })
            if User.objects.filter(email=email).exists():
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":"Este email esta en uso",
                    "back":request.POST
                })
            vv=validar_password(password1=password1,password2=password2)
            if vv!="OK":
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":vv,
                    "back":request.POST
                })
            try:
                nu=User(username=username,email=email)
                nu.set_password(password1)
                nu.save()
                nuu=models_admin.Usuario(userid=nu,tipo="Cliente")
                nuu.save()
                nc=models.Cliente(usuarioid=nuu,verificado=False,direccion=direccion)
                nc.save()
                nu = authenticate(request,username=username, password=password1)
                if nu is not None:
                    auth_login(request,nu)
                    return redirect("../../../../../../verificacion_correo/")
            except Exception as e:
                return render(request,"cliente/demo1.html",{
                    "productos":list(models_admin.Producto.objects.all()),
                    "Alerta":f"Error: {e}",
                    "back":request.POST
                })
        else:
            return redirect("../../../../../../../../")
        




class Perfil(View):
    def get(self,request):
        if request.user.is_authenticated:
            cliente=models.Cliente.objects.get(
                usuarioid=models_admin.Usuario.objects.get(userid=request.user)
            )
            return render(request,"cliente/Perfil.html",{
                "cliente":cliente
            })
        return redirect("../../../../../../../../../../../../")

    def post(self,request):
        if request.user.is_authenticated:
            cliente=models.Cliente.objects.get(
                usuarioid=models_admin.Usuario.objects.get(userid=request.user)
            )
            username=str(request.POST.get("username")).strip().lower()
            email=str(request.POST.get("email")).strip()
            direccion=str(request.POST.get("direccion")).strip()
            password0=request.POST.get("password0")
            password1=request.POST.get("password1")
            password2=request.POST.get("password2")
            if "" in [username,email,direccion]:
                return render(request,"cliente/Perfil.html",{
                    "cliente":cliente,"Alerta":"Todos los campos son obligatorios"
                })
            if username != request.user.username:
                request.user.username=username
                request.user.save()
            mod_email=False
            if email!=request.user.email:
                cliente.usuarioid.userid.email=email
                cliente.usuarioid.userid.save()
                cliente.verificado=False
                cliente.save()
                mod_email=True
            if direccion!=cliente.direccion:
                cliente.direccion=direccion
                cliente.save()
            
            if password0!="" or password1!="" or password2!="" :
                if "" in [password0,password1,password2]:
                    return render(request,"cliente/Perfil.html",{
                        "cliente":cliente,"Alerta":"Si desea cambiar la clave, todos los campos son obligatorios."
                    })
                if cliente.usuarioid.userid.check_password(password0):
                    v=validar_password(password1=password1,password2=password2)
                    if v!="OK":
                        return render(request,"cliente/Perfil.html",{
                            "cliente":cliente,"Alerta":v
                        })    
                    cliente.usuarioid.userid.set_password(password1)
                    cliente.usuarioid.userid.save()
                    user = authenticate(request,username=user.username, password=password1)
                    if user is not None:
                        auth_login(request,user)
                else:
                    return render(request,"cliente/Perfil.html",{
                        "cliente":cliente,"Alerta":"Contraseña actual incorrecta."
                    })
            print(mod_email)
            if mod_email==True:
                print(">>>>>>>>>>>>>>>>>>>>>>>")
                return redirect("../../../../../../../verificacion_correo/")
            else:
                return redirect("../../../../../../../../")
            
        return redirect("../../../../../../../../../../../../")







class Carrito(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                carrito=get_carrito(request.user)
                return render(request,"cliente/cart.html",{
                    "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito)
                })
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../")

    def post(self,request,carritoid):
        if request.user.is_authenticated:
            try:
                cliente=models.Cliente.objects.get(usuarioid=models_admin.Usuario.objects.get(userid=request.user))
                carrito=models.Carrito.objects.get(id=carritoid,clienteid=cliente)
                cantidad=int(request.POST.get("cantidad"))
                if cantidad>0 and cantidad<=carrito.productoid.cantidad:
                    carrito.cantidad=cantidad
                    carrito.save()
                    print(">>>>>>>>>>>>>>>>>>>>>>>>>")
            except Exception as e:
                print(e)
        return redirect("../../../../../../carrito/")
    
class Agregar_Carrito(View):
    def get(self,request,productoid):
        if request.user.is_authenticated:
            try:
                cliente=models.Cliente.objects.get(
                    usuarioid=models_admin.Usuario.objects.get(userid=request.user)
                )
                producto=models_admin.Producto.objects.get(id=productoid)
                if not models.Carrito.objects.filter(clienteid=cliente,productoid=producto).exists():
                    nc=models.Carrito(clienteid=cliente,productoid=producto,cantidad=1)
                    nc.save()
                return redirect("../../../../../../../../carrito/")
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../")
        
class Eliminar_Carrito(View):
    def get(self,request,carritoid):
        if request.user.is_authenticated:
            try:
                cliente=models.Cliente.objects.get(usuarioid=models_admin.Usuario.objects.get(userid=request.user))
                carrito=models.Carrito.objects.get(id=carritoid,clienteid=cliente)
                carrito.delete()
            except Exception as e:
                print(e)
        return redirect("../../../../../../carrito/")
    
class Efectuar_Compra(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                cliente=models.Cliente.objects.get(
                    usuarioid=models_admin.Usuario.objects.get(userid=request.user)
                )
                carrito=get_carrito(request.user)
                compra=None
                for cc in carrito:
                    print(">>>>>>>>>>>>>>>>")
                    print(cc.get("carrito").cantidad)
                    print(cc.get("carrito").productoid.cantidad)
                    if cc.get("carrito").cantidad <= cc.get("carrito").productoid.cantidad:
                        if compra==None:
                            compra=models.Compra(clienteid=cliente,pendiente=True)
                            compra.save()
                        
                        cc.get("carrito").productoid.cantidad-=cc.get("carrito").cantidad
                        cc.get("carrito").productoid.save()
                        detalle=models.Detalle(compraid=compra,productoid=cc.get("carrito").productoid,cantidad=cc.get("carrito").cantidad)
                        detalle.save()
                        print(cc.get('carrito'))
                        cc.get('carrito').delete()
            except Exception as e:
                print(e)
        return redirect("../../../../../../compras/")


class Compras(View):
    def get(self,request):
        if request.user.is_authenticated:
            try:
                carrito=get_carrito(request.user)
                return render(request,"cliente/cart-Comprobante.html",{
                    "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito),
                    "compras":get_Compras(request.user)
                })
            except Exception as e:
                print(e)
        return redirect("../../../../../../../../../")

########################################################################################################################
########################################################################################################################
########################################################################################################################
########################################################################################################################


class Contacto(View):
    def get(self,request):
        carrito=get_carrito(request.user)
        return render(request,"cliente/contact-us.html",{
            "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito),
        })
    def post(self,request):
        comentario=request.POST.get("comentario")
        nombre=None
        email=None
        m=None
        print(request.POST)
        if comentario=="":
            m="Todos los campos son obligatorios"
        if not request.user.is_authenticated:
            nombre=request.POST.get("nombre")
            email=request.POST.get("email")
            if "" in [nombre,email]:
                m="Todos los campos son obligatorios"
        if m==None:
            cliente=None
            try:
                cliente=models.Cliente.objects.get(usuarioid=models_admin.Usuario.objects.get(userid=request.user))
                nombre=cliente.usuarioid.userid.username
                email=cliente.usuarioid.userid.email
            except Exception:
                pass
            comentario=models.Comentario(clienteid=cliente,comentario=comentario,email=email,nombre=nombre)
            comentario.save()
            return redirect("../../../../../../../../../../")
        else:
            carrito=get_carrito(request.user)
            return render(request,"cliente/contact-us.html",{
                "carrito":carrito,"tamanio_carrito":tamanio_carrito(carrito),"total_monto":total_monto(carrito),
                "Alerta":m,
            })
