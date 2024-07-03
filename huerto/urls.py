from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from administrador import views as vwadmin
from cliente import views as cviews
urlpatterns = [
    path('admin/',include('administrador.urls')),
    path('dependiente/',include('Dependiente.urls')),
    path('',include('cliente.urls')),
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)