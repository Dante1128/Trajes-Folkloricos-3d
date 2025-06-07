from django import forms
from django.db import connection
from django.http import HttpResponse
from django.utils import timezone
from pyexpat.errors import messages
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render
from .models import Alquiler, Categoria, Garantia,  PagoAlquiler, Traje, Usuario
from .forms import  CategoriaForm, ClienteForm, ReservaCompletaForm, TrajeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from rest_framework import viewsets
from .models import Categoria
from .serializers import CategoriaSerializer, TrajeSerializer
import firebase_admin
from firebase_admin import credentials, storage


'''
Firebase Storage
'''
# Inicializa Firebase solo una vez (por ejemplo, en settings.py o al inicio de la vista)
cred = credentials.Certificate("d-trajes-folkloricos-firebase-adminsdk-fbsvc-f7abad95d9.json")
firebase_admin.initialize_app(cred, {
    'storageBucket': 'd-trajes-folkloricos.firebasestorage.app'
})





def subir_a_firebase(file_obj, nombre_archivo):
    bucket = storage.bucket()
    blob = bucket.blob(f'modelos_3d/{nombre_archivo}')
    blob.upload_from_file(file_obj)
    blob.make_public()  
    return blob.public_url











def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('inicio')

    formulario = AuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and formulario.is_valid():
        login(request, formulario.get_user())
        return redirect('inicio')

    return render(request, 'login.html', {'formulario': formulario})

def pagina_inicio(request):
    return render(request, 'cliente/inicio.html')

def clientes(request):
    mostrar_todos = request.GET.get('mostrar_todos') == 'on'

    if mostrar_todos:
        clientes = Usuario.objects.filter(rol='cliente')
    else:
        clientes = Usuario.objects.filter(rol='cliente', estado='activo')

    return render(request, 'cliente/clientes.html', {
        'clientes': clientes,
        'mostrar_todos': mostrar_todos
    })

def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            print("Cliente guardado correctamente")
            return redirect('clientes')
        else:
            print("Formulario con errores:")
            print(form.errors)
    else:
        form = ClienteForm()
    return render(request, 'cliente/crear_cliente.html', {'form': form})


def informacion_cliente(request, cliente_id):
    cliente = get_object_or_404(Usuario, id=cliente_id)
    return render(request, 'cliente/informacion_cliente.html', {'cliente': cliente})

def editar_cliente(request, cliente_id):
    cliente = Usuario.objects.get(id=cliente_id)

    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)
            print("Datos actualizados:")
            print(cliente.nombre, cliente.celular, cliente.estado, cliente.correo)
            cliente.save()
            return redirect('clientes')
        else:
            print("Errores:", form.errors)
    else:
        form = ClienteForm(instance=cliente)

    return render(request, 'cliente/editar_cliente.html', {'form': form, 'cliente': cliente})


def eliminar_cliente(request, cliente_id):
    cliente = get_object_or_404(Usuario, id=cliente_id)
    cliente.estado = 'inactivo'
    cliente.save()
    return redirect('clientes')

def catalogoTrajes(request):
     trajes = Traje.objects.select_related('categoria').all()
     return render(request, 'catalogo/catalogo.html', {
        'trajes': trajes
    })

def inventario(request):
    trajes = Traje.objects.select_related('categoria').all()
    return render(request, 'inventario/inventario.html', {
        'trajes': trajes
    })
def administracionCatalogo(request):
    categorias = Categoria.objects.all()  
    trajes = Traje.objects.all()
    return render(request, 'catalogo/administracionCatalogo.html', {
        'categorias': categorias,
        'trajes': trajes
        })

def agregarCategoria(request):
    if request.method == 'POST':
        form = form = CategoriaForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('administracionCatalogo') 
    else:
        form = CategoriaForm()
    return render(request, 'catalogo/agregar_categoria.html', {'form': form})

def editarCategoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)
    if request.method == 'POST':
        form = CategoriaForm(request.POST, request.FILES, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('administracionCatalogo')  
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'catalogo/editar_categoria.html', {'form': form, 'categoria': categoria})


def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)  
    categoria.delete()
    return redirect('administracionCatalogo') 


def registrar_traje(request):
    if request.method == 'POST':
        form = TrajeForm(request.POST, request.FILES)
        if form.is_valid():
            traje = form.save(commit=False)
            archivo = request.FILES.get('modelo_3d')
            if archivo:
                url = subir_a_firebase(archivo, archivo.name)  # Tu función personalizada
                traje.modelo_3d_url = url
            traje.save()
            return redirect('administracionCatalogo')
    else:
        form = TrajeForm()
    return render(request, 'catalogo/registrar_traje.html', {'form': form})

def editar_traje(request):
    return render(request, '')

def  eliminar_traje(request,id):
    trajes = get_object_or_404(Traje, id=id)
    trajes.delete()
    return redirect('administracionCatalogo')






def reserva(request):
    alquileres = Alquiler.objects.all()  # obtienes todos los registros
    return render(request, 'reserva/reserva.html', {'alquileres': alquileres})

def registrar_reserva(request):
    if request.method == 'POST':
        form = ReservaCompletaForm(request.POST)
        
        if form.is_valid():
            print("Formulario válido")  # <-- Aquí para confirmar que el form pasó
            
            try:
                # Guardar Alquiler
                alquiler = Alquiler.objects.create(
                    usuario=form.cleaned_data['usuario'],
                    traje=form.cleaned_data['traje'],
                    evento=form.cleaned_data['evento'],  # Solo texto aquí
                    fecha_reserva=timezone.now(),
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_final=form.cleaned_data['fecha_final'],
                    monto_total=form.cleaned_data['monto'],
                    estado=form.cleaned_data['estado'],  # Asegúrate que 'estado' está en tu modelo
                    metodo_pago=form.cleaned_data['metodo_pago'],
                )
            except Exception as e:
                print("Error al crear alquiler:", e)
                # Opcional: puedes devolver un mensaje de error o redirigir a otra página aquí

            # Guardar Pago
            PagoAlquiler.objects.create(
                alquiler=alquiler,
                monto=form.cleaned_data['monto'],
                fecha_pago=timezone.now(),
                metodo_pago=form.cleaned_data['metodo_pago'],
                estado=form.cleaned_data['estado_pago'],

                referencia=form.cleaned_data['referencia'],
            )
            
            # Guardar Garantia
            Garantia.objects.create(
                alquiler=alquiler,
                usuario=form.cleaned_data['usuario'],
                estado=form.cleaned_data['estado_garantia'],
                descripcion=form.cleaned_data['descripcion_garantia'],
            )
            
            return redirect('reserva')  # <--- Aquí va la redirección al final del proceso exitoso

        else:
            print("Errores en el formulario:", form.errors)  # <-- Aquí para ver errores si el form no es válido
    else:
        form = ReservaCompletaForm()
        
    return render(request, 'reserva/registrar_reserva.html', {'form': form})



def editar_reserva(request, reserva_id):
    alquiler = get_object_or_404(Alquiler, pk=reserva_id)

    if request.method == 'POST':
        form = ReservaCompletaForm(request.POST)
        if form.is_valid():
           
            alquiler.usuario = form.cleaned_data['usuario']
            alquiler.traje = form.cleaned_data['traje']
            alquiler.evento = form.cleaned_data['evento']
            alquiler.fecha_inicio = form.cleaned_data['fecha_inicio']
            alquiler.fecha_final = form.cleaned_data['fecha_final']
            alquiler.estado = form.cleaned_data['estado']
            alquiler.save()

          
            pago = PagoAlquiler.objects.filter(alquiler=alquiler).first()
            if pago:
                pago.monto = form.cleaned_data['monto']
                pago.metodo_pago = form.cleaned_data['metodo_pago']
                pago.estado = form.cleaned_data['estado_pago']
                pago.referencia = form.cleaned_data['referencia']
                pago.save()
            else:
              
                PagoAlquiler.objects.create(
                    alquiler=alquiler,
                    monto=form.cleaned_data['monto'],
                    fecha_pago=timezone.now(),
                    metodo_pago=form.cleaned_data['metodo_pago'],
                    estado=form.cleaned_data['estado_pago'],
                    referencia=form.cleaned_data['referencia'],
                )

         

            return redirect('reserva')  

    else:
      
        pago = PagoAlquiler.objects.filter(alquiler=alquiler).first()
        initial_data = {
            'usuario': alquiler.usuario,
            'traje': alquiler.traje,
            'evento': alquiler.evento,
            'fecha_inicio': alquiler.fecha_inicio,
            'fecha_final': alquiler.fecha_final,
            'estado': alquiler.estado,
            'monto': pago.monto if pago else None,
            'metodo_pago': pago.metodo_pago if pago else None,
            'estado_pago': pago.estado if pago else None,
            'referencia': pago.referencia if pago else '',
            
        }
        form = ReservaCompletaForm(initial=initial_data)

    return render(request, 'reserva/editar_reserva.html', {'form': form, 'alquiler': alquiler})

def cerrar_sesion(request):
    logout(request)
    return redirect('login')



'''
Serializers for the API views
'''

class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer

    def get_serializer_context(self):
        return {'request': self.request}
    
class TrajeViewSet(viewsets.ModelViewSet):
    queryset = Traje.objects.all()
    serializer_class = TrajeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset