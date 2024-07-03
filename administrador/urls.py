from django.urls import path
from . import views

urlpatterns = [
    path('',views.Login.as_view()),
    path('logout/',views.cerrarsesion),
    path('home/',views.Index.as_view()),
    path('mercancias/',views.Gestionar_Mercancias.as_view()),
    path('mercancias/modificar/<int:productoid>',views.Modificar_Producto.as_view()),
    path('mercancias/agregar/',views.Agregar_Producto.as_view()),
    path('mercancias/eliminar/<int:productoid>',views.Eliminar_Producto.as_view()),

    path('exportar_inventario/',views.exportar_inventario),

    path('gestion_usuarios/',views.Gestionar_Usuarios.as_view()),
    path('gestion_usuarios/agregar/',views.Agregar_Usuario.as_view()),
    path('gestion_usuarios/eliminar/<int:empleadoid>',views.Eliminar_usuario.as_view()),

    path('reportes/',views.exportar_reporte),
    
    path('correo/',views.Correo.as_view()),
    path('correo/responder/<int:comentarioid>/',views.Responder_Comentario.as_view()),
    path('correo/eliminar/<int:comentarioid>/',views.Eliminar_Comentario.as_view()),

    path('perfil/',views.Perfil.as_view()),
]
