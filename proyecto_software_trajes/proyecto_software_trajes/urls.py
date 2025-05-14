from django.contrib import admin
from django.urls import path
from cuenta.views import administracionCatalogo, agregarCategoria, catalogoTrajes, clientes, crear_cliente, editar_cliente, editar_traje, editarCategoria, eliminar_categoria, eliminar_cliente, informacion_cliente, iniciar_sesion, cerrar_sesion, inventario, pagina_inicio, registrar_traje, reserva
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', iniciar_sesion, name='login'),
    path('inicio/', pagina_inicio, name='inicio'),
    path('clientes/',clientes , name='clientes' ),
    path('crear_cliente/',crear_cliente, name='crear_cliente'),
    path('informacion_cliente/<int:cliente_id>/', informacion_cliente, name='informacion_cliente'),
    path('editar_cliente/<int:cliente_id>', editar_cliente,name='editar_cliente'),
    path('eliminar_cliente/<int:cliente_id>/', eliminar_cliente, name='eliminar_cliente'),
    path('inventario/',inventario, name='inventario'),
    path('catalogoTrajes/', catalogoTrajes, name='catalogoTrajes'),
    path('administracionCatalogo/', administracionCatalogo, name='administracionCatalogo'),
    path('reserva/',reserva,name='reserva'),
    path('agregarCategoria/', agregarCategoria, name='agregar_categoria'),
    path('editar_categoria/<int:categoria_id>/',editarCategoria, name='editar_categoria'),
    path('eliminar_categoria/<int:id>/',eliminar_categoria, name='eliminar_categoria'),
    path('registrar_traje/', registrar_traje, name='registrar_traje'),
    path('editar_traje/<int:id>', editar_traje, name= editar_traje),
    path('cerrar/', cerrar_sesion, name='cerrar_sesion'),
    


]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)