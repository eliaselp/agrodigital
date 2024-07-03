from django.urls import path
from . import views

urlpatterns = [
    path('',views.Index.as_view()),
    path('categoria/<str:categoria>/',views.Categoria.as_view()),
    path('login/',views.Login.as_view()),
    path('logout/',views.Logout.as_view()),
    path('registrar/',views.Registro.as_view()),
    path('verificacion_correo/',views.Verificacion.as_view()),
    path('perfil/',views.Perfil.as_view()),

    path('agregar_carrito/<int:productoid>/',views.Agregar_Carrito.as_view()),
    path('carrito/',views.Carrito.as_view()),
    path('carrito/<int:carritoid>',views.Carrito.as_view()),
    path('eliminar_carrito/<int:carritoid>',views.Eliminar_Carrito.as_view()),

    path('compras/',views.Compras.as_view()),
    path('efectuar_compra/',views.Efectuar_Compra.as_view()),

    path("contacto/",views.Contacto.as_view()),
]
