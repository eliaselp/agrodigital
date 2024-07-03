from django.db import models

from administrador import models as models_admin
# Create your models here.

class Cliente(models.Model):
    usuarioid=models.OneToOneField(models_admin.Usuario,on_delete=models.CASCADE,null=False,blank=False)
    tocken=models.CharField(max_length=200,null=True,blank=True)
    verificado=models.BooleanField(null=False,blank=False)
    direccion=models.TextField(null=False,blank=False)


class Carrito(models.Model):
    clienteid=models.ForeignKey(Cliente,on_delete=models.CASCADE,null=False,blank=False)
    productoid=models.ForeignKey(models_admin.Producto,on_delete=models.CASCADE,null=True,blank=False)
    cantidad=models.IntegerField(null=True,blank=False)


class Compra(models.Model):
    clienteid=models.ForeignKey(Cliente,on_delete=models.CASCADE,null=False,blank=False)
    pendiente=models.BooleanField(null=False,blank=False)
    fecha=models.DateField(null=False,auto_now=True)


class Detalle(models.Model):
    compraid=models.ForeignKey(Compra,on_delete=models.CASCADE,null=False,blank=False)
    productoid=models.ForeignKey(models_admin.Producto,on_delete=models.CASCADE,null=True,blank=False)
    cantidad=models.IntegerField(null=True,blank=False)


class Comentario(models.Model):
    clienteid=models.ForeignKey(Cliente,null=True,on_delete=models.CASCADE,blank=True)
    comentario=models.TextField(null=False,blank=False)
    email=models.EmailField(null=False,blank=False)
    nombre=models.CharField(null=False,blank=False,max_length=100)