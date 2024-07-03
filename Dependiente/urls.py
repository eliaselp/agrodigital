from django.urls import path
from . import views
from administrador import views as admin_views
urlpatterns = [
    path('',admin_views.Login.as_view()),
    path('logout/',admin_views.cerrarsesion),
    path('home/',views.Index.as_view()),
    path('perfil/',admin_views.Perfil.as_view()),
    path('ventas/',views.Ventas.as_view()),
    path('ventas/entrega/<int:ventaid>',views.Hacer_Entrega.as_view()),
    path('reporte_ventas/',views.generar_reporte_ventas)
]
