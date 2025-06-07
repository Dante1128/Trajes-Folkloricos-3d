from django import views
from django.contrib import admin
from django.urls import include, path
from cuenta.views import CategoriaViewSet, TrajeViewSet, administracionCatalogo, agregarCategoria, catalogoTrajes,  clientes, crear_cliente, editar_cliente, editar_reserva, editar_traje, editarCategoria, eliminar_categoria, eliminar_cliente, eliminar_traje, informacion_cliente, iniciar_sesion, cerrar_sesion, inventario, pagina_inicio, registrar_reserva, registrar_traje, reserva
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'categorias', CategoriaViewSet, basename='categoria')
router.register(r'trajes', TrajeViewSet, basename='traje')

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
    path('agregarCategoria/', agregarCategoria, name='agregar_categoria'),
    path('editar_categoria/<int:categoria_id>/',editarCategoria, name='editar_categoria'),
    path('eliminar_categoria/<int:id>/',eliminar_categoria, name='eliminar_categoria'),
    path('registrar_traje/', registrar_traje, name='registrar_traje'),
    path('editar_traje/<int:id>', editar_traje, name='editar_traje'),
    path('eliminar_traje/<int:id>/', eliminar_traje, name='eliminar_traje'),
    path('reserva/',reserva,name='reserva'),
    path('registrar_reserva/',registrar_reserva,name='registrar_reserva'),
    path('editar_reserva/<int:reserva_id>/', editar_reserva, name='editar_reserva'),
    path('cerrar/', cerrar_sesion, name='cerrar_sesion'),

    # API URLs
     path('api/', include(router.urls)),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)