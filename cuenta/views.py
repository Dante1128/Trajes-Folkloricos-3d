from datetime import datetime
from itertools import count
from django import forms
from django.db import connection
from django.http import HttpResponse, FileResponse, HttpResponseBadRequest, JsonResponse
from django.utils import timezone
from pyexpat.errors import messages
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render
from .models import Alquiler, Garantia, PagoAlquiler, Traje, Usuario
from .forms import ClienteForm, ReservaCompletaForm, TrajeForm, AlquilarTrajeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from rest_framework import viewsets
from .serializers import TrajeSerializer, UsuarioSerializer
import firebase_admin
from firebase_admin import credentials, storage
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Count
from cryptography.fernet import Fernet
import os
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from django.http import HttpResponse
from django.shortcuts import render
import os
from firebase_admin import auth  # Importar Firebase Admin SDK para verificar tokens
from django.views.decorators.csrf import csrf_exempt
import json



'''
Firebase Storage
'''

if not firebase_admin._apps:
    auth_cred = credentials.Certificate("c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\trajes-folkloricos-firebase-adminsdk-fbsvc-d1de3d505e.json")
    firebase_admin.initialize_app(auth_cred)


storage_cred = credentials.Certificate("c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\d-trajes-folkloricos-firebase-adminsdk-fbsvc-f7abad95d9.json")
storage_app = firebase_admin.initialize_app(storage_cred, {
    'storageBucket': 'd-trajes-folkloricos.firebasestorage.app' 
}, name='storage_app')

def subir_a_firebase(file_obj, nombre_archivo):
   
    bucket = storage.bucket(app=storage_app)
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
@login_required  
def clientes(request):
    mostrar_todos = request.GET.get('mostrar_todos') == 'on'

    if mostrar_todos not in [True, False]:
        # Si alguien manipula manualmente la URL con valores extraños
        return HttpResponseBadRequest("Parámetro inválido.")

    if mostrar_todos:
        clientes = Usuario.objects.filter(rol='cliente')
    else:
        clientes = Usuario.objects.filter(rol='cliente', estado='activo')

    return render(request, 'cliente/clientes.html', {
        'clientes': clientes,
        'mostrar_todos': mostrar_todos
    })

@login_required
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
    """
    Vista para mostrar el catálogo de trajes.
    """
    trajes = Traje.objects.all()  # Eliminé la referencia a 'categoria'
    return render(request, 'catalogo/catalogo.html', {
        'trajes': trajes
    })

def inventario(request):
    """
    Vista para mostrar el inventario de trajes.
    """
    trajes = Traje.objects.all()  # Eliminé la referencia a 'categoria'
    return render(request, 'inventario/inventario.html', {
        'trajes': trajes
    })
def administracionCatalogo(request):
    """
    Vista para administrar el catálogo de trajes.
    """
    trajes = Traje.objects.all()  # Eliminé la consulta de categorías
    return render(request, 'catalogo/administracionCatalogo.html', {
        'trajes': trajes
    })


def registrar_traje(request):
    if request.method == 'POST':
        form = TrajeForm(request.POST, request.FILES)
        if form.is_valid():
            traje = form.save(commit=False)
            archivo = request.FILES.get('modelo_3d')
            if archivo:
                url = subir_a_firebase(archivo, archivo.name)  
                traje.modelo_3d_url = url
            traje.save()
            return redirect('administracionCatalogo')
    else:
        form = TrajeForm()
    return render(request, 'catalogo/registrar_traje.html', {'form': form})

def editar_traje(request, traje_id):
    traje = get_object_or_404(Traje, id=traje_id)
    if request.method == 'POST':
        form = TrajeForm(request.POST, request.FILES, instance=traje)
        if form.is_valid():
            traje = form.save(commit=False)
            archivo = request.FILES.get('modelo_3d')
            if archivo:
                url = subir_a_firebase(archivo, archivo.name)  
                traje.modelo_3d_url = url
            traje.save()
            return redirect('administracionCatalogo')
    else:
        form = TrajeForm(instance=traje)
    return render(request, 'catalogo/editar_traje.html', {'form': form, 'traje': traje})

def  eliminar_traje(request,id):
    trajes = get_object_or_404(Traje, id=id)
    trajes.delete()
    return redirect('administracionCatalogo')






def reserva(request):
    alquileres = Alquiler.objects.all() 
    return render(request, 'reserva/reserva.html', {'alquileres': alquileres})

def registrar_reserva(request):
    if request.method == 'POST':
        form = ReservaCompletaForm(request.POST)
        
        if form.is_valid():
            print("Formulario válido")  
            
            try:
         
                alquiler = Alquiler.objects.create(
                    usuario=form.cleaned_data['usuario'],
                    traje=form.cleaned_data['traje'],
                    evento=form.cleaned_data['evento'],  
                    fecha_reserva=timezone.now(),
                    fecha_inicio=form.cleaned_data['fecha_inicio'],
                    fecha_final=form.cleaned_data['fecha_final'],
                    monto_total=form.cleaned_data['monto'],
                    estado=form.cleaned_data['estado'], 
                    metodo_pago=form.cleaned_data['metodo_pago'],
                )
            except Exception as e:
                print("Error al crear alquiler:", e)
    
            PagoAlquiler.objects.create(
                alquiler=alquiler,
                monto=form.cleaned_data['monto'],
                fecha_pago=timezone.now(),
                metodo_pago=form.cleaned_data['metodo_pago'],
                estado=form.cleaned_data['estado_pago'],

                referencia=form.cleaned_data['referencia'],
            )
            
       
            Garantia.objects.create(
                alquiler=alquiler,
                usuario=form.cleaned_data['usuario'],
                estado=form.cleaned_data['estado_garantia'],
                descripcion=form.cleaned_data['descripcion_garantia'],
            )
            
            return redirect('reserva')  

        else:
            print("Errores en el formulario:", form.errors)  
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

@login_required
def alquilar_traje(request, traje_id):
    traje = get_object_or_404(Traje, id=traje_id)

    if request.method == 'POST':
        form = AlquilarTrajeForm(request.POST)
        if form.is_valid():
            alquiler = form.save(commit=False)
            alquiler.traje = traje
            alquiler.usuario = form.cleaned_data['cliente']
            alquiler.cantidad = form.cleaned_data['cantidad']
            alquiler.save()

            Garantia.objects.create(
                alquiler=alquiler,
                usuario=form.cleaned_data['cliente'],
                estado=form.cleaned_data['estado_garantia'],
                descripcion=form.cleaned_data['descripcion_garantia'],
            )
            return redirect('catalogoTrajes')
    else:
        form = AlquilarTrajeForm()

    return render(request, 'catalogo/alquilar_traje.html', {
        'form': form,
        'traje': traje
    })

@login_required
def mis_alquileres(request):
    alquileres = Alquiler.objects.select_related('usuario', 'traje').filter(estado='alquilado')
    garantias = {g.alquiler_id: g for g in Garantia.objects.filter(alquiler__in=alquileres)}
    return render(request, 'catalogo/mis_alquileres.html', {
        'alquileres': alquileres,
        'garantias': garantias
    })

@login_required
@require_POST
def editar_estado_garantia(request, garantia_id):
    garantia = get_object_or_404(Garantia, id=garantia_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Garantia.ESTADO_CHOICES):
        garantia.estado = nuevo_estado
        garantia.save()
    return redirect('mis_alquileres')

@login_required
@require_POST
def editar_estado_reserva(request, alquiler_id):
    alquiler = get_object_or_404(Alquiler, id=alquiler_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(Alquiler.ESTADO_CHOICES):
        alquiler.estado = nuevo_estado
        alquiler.save()
    return redirect('reserva')

@login_required
@require_POST
def editar_estado_pago(request, pago_id):
    pago = get_object_or_404(PagoAlquiler, id=pago_id)
    nuevo_estado = request.POST.get('estado')
    if nuevo_estado in dict(PagoAlquiler.ESTADO_CHOICES):
        pago.estado = nuevo_estado
        pago.save()
    return redirect('reserva')

@login_required
def informes_reportes(request):
    
    fecha_desde_str = request.GET.get('fecha_desde')
    fecha_hasta_str = request.GET.get('fecha_hasta')

    try:
        fecha_desde = datetime.strptime(fecha_desde_str, "%Y-%m-%d").date() if fecha_desde_str else datetime.today().date()
        fecha_hasta = datetime.strptime(fecha_hasta_str, "%Y-%m-%d").date() if fecha_hasta_str else datetime.today().date()
    except ValueError:
        fecha_desde = fecha_hasta = datetime.today().date()

   
    fecha_hasta = datetime.combine(fecha_hasta, datetime.max.time())

   
    alquileres = Alquiler.objects.filter(fecha_inicio__range=[fecha_desde, fecha_hasta], estado='alquilado')
    reservas = Alquiler.objects.filter(fecha_inicio__range=[fecha_desde, fecha_hasta], estado='reservado')

    
    total_trajes_alquilados = alquileres.aggregate(total=Count('cantidad'))['total']
    total_trajes_reservados = reservas.aggregate(total=Count('cantidad'))['total']

    for alquiler in alquileres:
        alquiler.monto_total = f"{alquiler.monto_total:.2f} Bs"
    for reserva in reservas:
        reserva.monto_total = f"{reserva.monto_total:.2f} Bs"

    context = {
        'fecha_desde': fecha_desde,
        'fecha_hasta': fecha_hasta,
        'alquileres': alquileres,
        'reservas': reservas,
        'total_trajes_alquilados': total_trajes_alquilados or 0,
        'total_trajes_reservados': total_trajes_reservados or 0,
    }
    return render(request, 'informes_reportes.html', context)

def informacion_alquiler(request, alquiler_id):
    alquiler = get_object_or_404(Alquiler, id=alquiler_id)
    garantia = Garantia.objects.filter(alquiler=alquiler).first()
    pago = PagoAlquiler.objects.filter(alquiler=alquiler).first()
    return render(request, 'catalogo/informacion_alquiler.html', {
        'alquiler': alquiler,
        'garantia': garantia,
        'pago': pago
    })

def informacion_reserva(request, reserva_id):
    alquiler = get_object_or_404(Alquiler, id=reserva_id)
    garantia = Garantia.objects.filter(alquiler=alquiler).first()
    pago = PagoAlquiler.objects.filter(alquiler=alquiler).first()
    return render(request, 'reserva/informacion_reserva.html', {
        'alquiler': alquiler,
        'garantia': garantia,
        'pago': pago
    })



'''
Serializers for the API views
'''

class TrajeViewSet(viewsets.ModelViewSet):
    queryset = Traje.objects.all()
    serializer_class = TrajeSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        categoria_id = self.request.query_params.get('categoria')
        if categoria_id:
            queryset = queryset.filter(categoria_id=categoria_id)
        return queryset


@login_required
def criptografia(request):
    return render(request, 'criptografia/criptografia.html')

@login_required
def cifrar_pdf(request):
 
    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo = request.FILES['archivo']
        clave = request.POST.get('clave', '').encode('utf-8')

        if len(clave) != 16:
            return HttpResponse("La clave debe tener exactamente 16 caracteres.", status=400)

       
        contenido = archivo.read()
        cipher = AES.new(clave, AES.MODE_CBC)
        iv = cipher.iv
        contenido_cifrado = iv + cipher.encrypt(pad(contenido, AES.block_size))

        ruta_archivo = os.path.join('c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\cuenta\\static\\reports', 'archivo_cifrado.txt')
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, 'wb') as archivo_cifrado:
            archivo_cifrado.write(contenido_cifrado) 
        return FileResponse(open(ruta_archivo, 'rb'), as_attachment=True, filename='archivo_cifrado.txt')
    return render(request, 'criptografia/cifrar_pdf.html')

@login_required
def descifrar_pdf(request):
    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo = request.FILES['archivo']
        clave = request.POST.get('clave', '').encode('utf-8')
        if len(clave) != 16:
            return HttpResponse("La clave debe tener exactamente 16 caracteres.", status=400)

        contenido = archivo.read()
        iv = contenido[:16]
        contenido_cifrado = contenido[16:]
        cipher = AES.new(clave, AES.MODE_CBC, iv)
        try:
            contenido_descifrado = unpad(cipher.decrypt(contenido_cifrado), AES.block_size)
        except ValueError:
            return HttpResponse("La clave o el archivo son incorrectos.", status=400)
        ruta_archivo = os.path.join('c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\cuenta\\static\\reports', 'archivo_descifrado.pdf')
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, 'wb') as archivo_descifrado:
            archivo_descifrado.write(contenido_descifrado)
        return FileResponse(open(ruta_archivo, 'rb'), as_attachment=True, filename='archivo_descifrado.pdf')
    return render(request, 'criptografia/descifrar_pdf.html')

@login_required
def generar_reporte_cifrado(request):

    if request.method == 'POST':
       
        contenido_reporte = "Este es el contenido del reporte generado dinámicamente."
       
        clave = Fernet.generate_key()  
        cipher_suite = Fernet(clave)
        contenido_cifrado = cipher_suite.encrypt(contenido_reporte.encode())

        ruta_carpeta = 'c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\cuenta\\static\\reports'
        ruta_archivo = os.path.join(ruta_carpeta, 'reporte_cifrado.txt')
   
        os.makedirs(ruta_carpeta, exist_ok=True)

        with open(ruta_archivo, 'wb') as archivo:
            archivo.write(contenido_cifrado)

        return FileResponse(open(ruta_archivo, 'rb'), as_attachment=True, filename='reporte_cifrado.txt')
    return render(request, 'criptografia/generar_reporte.html')

@login_required
def cifrar_archivo(request):

    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo = request.FILES['archivo']
        clave = request.POST.get('clave', '').encode('utf-8')

        if len(clave) != 16:
            return HttpResponse("La clave debe tener exactamente 16 caracteres.", status=400)
        contenido = archivo.read()
        cipher = AES.new(clave, AES.MODE_CBC)
        iv = cipher.iv
        contenido_cifrado = iv + cipher.encrypt(pad(contenido, AES.block_size))
        ruta_archivo = os.path.join('c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\cuenta\\static\\reports', 'archivo_cifrado.bin')
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, 'wb') as archivo_cifrado:
            archivo_cifrado.write(contenido_cifrado)

        return HttpResponse("Archivo cifrado correctamente. Descárgalo desde la carpeta 'reports'.")
    return render(request, 'criptografia/cifrar_archivo.html')

@login_required
def descifrar_archivo(request):
   
    if request.method == 'POST' and 'archivo' in request.FILES:
        archivo = request.FILES['archivo']
        clave = request.POST.get('clave', '').encode('utf-8')

        if len(clave) != 16:
            return HttpResponse("La clave debe tener exactamente 16 caracteres.", status=400)
        contenido = archivo.read()
        iv = contenido[:16]
        contenido_cifrado = contenido[16:]
        cipher = AES.new(clave, AES.MODE_CBC, iv)
        try:
            contenido_descifrado = unpad(cipher.decrypt(contenido_cifrado), AES.block_size)
        except ValueError:
            return HttpResponse("La clave o el archivo son incorrectos.", status=400)
        ruta_archivo = os.path.join('c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\cuenta\\static\\reports', 'archivo_descifrado.txt')
        os.makedirs(os.path.dirname(ruta_archivo), exist_ok=True)
        with open(ruta_archivo, 'wb') as archivo_descifrado:
            archivo_descifrado.write(contenido_descifrado)

        return HttpResponse("Archivo descifrado correctamente. Descárgalo desde la carpeta 'reports'.")
    return render(request, 'criptografia/descifrar_archivo.html')

@csrf_exempt
def registrar_cliente_flutter(request):
    print(f"🔥 Método recibido: {request.method}")  # Depuración

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            firebase_token = data.get('firebase_token')
            print(f"🔥 Token recibido: {firebase_token}")  # Depuración

      
            decoded_token = auth.verify_id_token(firebase_token)
            print(f"🔥 Token decodificado: {decoded_token}") 

            uid = decoded_token['uid']
            print(f"🔥 UID decodificado: {uid}")  

            # Agregar UID al cuerpo de los datos
            data['uid'] = uid

            # Validar y guardar los datos del cliente usando el serializer
            serializer = UsuarioSerializer(data=data)
            if serializer.is_valid():
                serializer.save(rol='cliente', estado='activo')  # Forzar valores predeterminados
                return JsonResponse({'message': 'Cliente registrado exitosamente.'}, status=201)
            else:
                print(f"🔥 Errores del serializer: {serializer.errors}")  # Depuración
                return JsonResponse(serializer.errors, status=400)

        except auth.InvalidIdTokenError as e:
            print(f"🔥 Token de Firebase inválido: {str(e)}")  # Depuración
            return JsonResponse({'message': 'Token de Firebase inválido.'}, status=400)
        except Exception as e:
            print(f"🔥 Error: {str(e)}")  # Depuración
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def registrar_reserva_flutter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Validar datos requeridos
            usuario_id = data.get('usuario_id')
            traje_id = data.get('traje_id')
            evento = data.get('evento', 'Sin evento')  # Valor predeterminado
            fecha_inicio = data.get('fecha_inicio')
            fecha_final = data.get('fecha_final')
            monto = data.get('monto', 0.0)  # Valor predeterminado
            metodo_pago = data.get('metodo_pago', 'Pendiente')  # Valor predeterminado
            estado_pago = data.get('estado_pago', 'Pendiente')  # Valor predeterminado
            referencia = data.get('referencia', '')  # Valor predeterminado
            estado_garantia = data.get('estado_garantia', 'no_devuelto')  # Valor predeterminado
            descripcion_garantia = data.get('descripcion_garantia', '')  # Valor predeterminado
            cantidad = data.get('cantidad', 1)  # Valor predeterminado
            talla = data.get('talla', 'M')  # Valor predeterminado

            # Validar campos obligatorios
            if not all([usuario_id, traje_id, fecha_inicio, fecha_final]):
                return JsonResponse({'message': 'Faltan datos requeridos.'}, status=400)

            # Obtener usuario y traje
            usuario = get_object_or_404(Usuario, id=usuario_id)
            traje = get_object_or_404(Traje, id=traje_id)

            # Crear la reserva
            alquiler = Alquiler.objects.create(
                usuario=usuario,
                traje=traje,
                evento=evento,
                fecha_reserva=timezone.now(),
                fecha_inicio=fecha_inicio,
                fecha_final=fecha_final,
                monto_total=monto,
                estado='reservado',
                metodo_pago=metodo_pago,
                cantidad=cantidad,
                talla=talla,
            )

            # Crear el pago
            PagoAlquiler.objects.create(
                alquiler=alquiler,
                monto=monto,
                fecha_pago=timezone.now(),
                metodo_pago=metodo_pago,
                estado=estado_pago,
                referencia=referencia,
            )

            # Crear la garantía
            Garantia.objects.create(
                alquiler=alquiler,
                usuario=usuario,
                estado=estado_garantia,
                descripcion=descripcion_garantia,
            )

            return JsonResponse({'message': 'Reserva registrada exitosamente.'}, status=201)

        except Exception as e:
            print(f"🔥 Error al registrar reserva: {str(e)}")
            return JsonResponse({'message': f'Error: {str(e)}'}, status=500)

    return JsonResponse({'message': 'Método no permitido.'}, status=405)

@csrf_exempt
def detalles_reserva(request, reserva_id):
    try:
        # Obtener la reserva
        alquiler = get_object_or_404(Alquiler, id=reserva_id)
        garantia = Garantia.objects.filter(alquiler=alquiler).first()
        pago = PagoAlquiler.objects.filter(alquiler=alquiler).first()

        # Construir la respuesta JSON
        detalles = {
            'evento': alquiler.evento,
            'fecha_inicio': alquiler.fecha_inicio.strftime('%Y-%m-%d'),
            'fecha_final': alquiler.fecha_final.strftime('%Y-%m-%d'),
            'cantidad_trajes': alquiler.cantidad,
            'talla': alquiler.talla,
            'monto_total': f"{alquiler.monto_total:.2f} Bs",
            'estado': alquiler.estado,
            'metodo_pago': alquiler.metodo_pago,
            'referencia': pago.referencia if pago else None,
            'estado_pago': pago.estado if pago else None,
            'estado_garantia': garantia.estado if garantia else None,
            'descripcion_garantia': garantia.descripcion if garantia else None,
        }

        return JsonResponse(detalles, status=200)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)