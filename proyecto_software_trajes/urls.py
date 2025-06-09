from django import views
from django.contrib import admin
from django.urls import include, path
from cuenta.views import CategoriaViewSet, TrajeViewSet, administracionCatalogo, agregarCategoria, catalogoTrajes,  clientes, crear_cliente, editar_cliente, editar_reserva, editar_traje, editarCategoria, eliminar_categoria, eliminar_cliente, eliminar_traje, informacion_alquiler, informacion_cliente, informacion_reserva, iniciar_sesion, cerrar_sesion, inventario, pagina_inicio, registrar_reserva, registrar_traje, reserva, alquilar_traje, mis_alquileres, editar_estado_garantia, editar_estado_reserva, editar_estado_pago, informes_reportes, generar_reporte_cifrado, cifrar_archivo, descifrar_archivo, criptografia, cifrar_pdf, descifrar_pdf
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
    path('editar_traje/<int:traje_id>/', editar_traje, name='editar_traje'),
    path('eliminar_traje/<int:id>/', eliminar_traje, name='eliminar_traje'),
    path('reserva/',reserva,name='reserva'),
    path('registrar_reserva/',registrar_reserva,name='registrar_reserva'),
    path('editar_reserva/<int:alquiler_id>/', editar_estado_reserva, name='editar_estado_reserva'),
    path('cerrar/', cerrar_sesion, name='cerrar_sesion'),
    path('alquilar_traje/<int:traje_id>/', alquilar_traje, name='alquilar_traje'),
    path('mis_alquileres/', mis_alquileres, name='mis_alquileres'),
    path('editar_estado_garantia/<int:garantia_id>/', editar_estado_garantia, name='editar_estado_garantia'),
    path('editar_estado_pago/<int:pago_id>/', editar_estado_pago, name='editar_estado_pago'),
    path('informes_reportes/', informes_reportes, name='informes_reportes'),
    path('informacion_alquiler/<int:alquiler_id>/', informacion_alquiler, name='informacion_alquiler'),
    path('informacion_reserva/<int:reserva_id>/', informacion_reserva, name='informacion_reserva'),
    path('generar_reporte_cifrado/', generar_reporte_cifrado, name='generar_reporte_cifrado'),
    path('cifrar_archivo/', cifrar_archivo, name='cifrar_archivo'),
    path('descifrar_archivo/', descifrar_archivo, name='descifrar_archivo'),
    path('criptografia/', criptografia, name='criptografia'),
    path('cifrar_pdf/', cifrar_pdf, name='cifrar_pdf'),
    path('descifrar_pdf/', descifrar_pdf, name='descifrar_pdf'),

    # API URLs
     path('api/', include(router.urls)),
    
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)