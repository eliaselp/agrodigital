from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Usuario(models.Model):
    userid=models.OneToOneField(User, on_delete=models.CASCADE,null=False)
    tipo=models.CharField(max_length=50)


class Dependiente(models.Model):
    nombre=models.CharField(max_length=200,null=False,blank=False)
    apellidos=models.CharField(max_length=200,null=False,blank=False)
    telefono=models.TextField(null=False,blank=False)
    usuarioid=models.OneToOneField(Usuario,on_delete=models.CASCADE,null=False,blank=False)


class Producto(models.Model):
    nombre=models.CharField(max_length=50,null=False,blank=False)
    tipo=models.CharField(max_length=50,null=False,blank=False)
    cantidad=models.IntegerField(null=False,blank=False)
    precio=models.FloatField(null=False,blank=False)
    ultimo_update=models.DateField(null=False,auto_now=True)
    urlimagen=models.CharField(max_length=300,null=False,blank=False)

