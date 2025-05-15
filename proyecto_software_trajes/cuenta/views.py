from pyexpat.errors import messages
from django.forms import ModelForm
from django.shortcuts import get_object_or_404, render
from .models import Categoria, Modelo3D, Traje, Usuario
from .forms import CategoriaForm, ClienteForm, TrajeForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect

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
            print("✅ Cliente guardado correctamente")
            return redirect('clientes')
        else:
            print("❌ Formulario con errores:")
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
    return render(request, "catalogo/catalogo.html")

def reserva(request):
    return render(request, 'cliente/reserva.html' )

def inventario(request):
    return render(request, 'inventario/inventario.html' )

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
            return redirect('administracionCatalogo')  # Redirige después de guardar
    else:
        form = CategoriaForm(instance=categoria)
    return render(request, 'catalogo/editar_categoria.html', {'form': form, 'categoria': categoria})


def eliminar_categoria(request, id):
    categoria = get_object_or_404(Categoria, id=id)  # Aquí se usa `id`, NO `categoria_id`
    categoria.delete()
    return redirect('administracionCatalogo') 


def registrar_traje(request):
    if request.method == 'POST':
        form = TrajeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('administracionCatalogo')  # Asegúrate de que esta URL esté definida en urls.py
    else:
        form = TrajeForm()

    return render(request, 'catalogo/registrar_traje.html', {'form': form})


def editar_traje(request):
    return render(request, '')

def  eliminar_traje(request,id):
    trajes = get_object_or_404(Traje, id=id)
    trajes.delete()
    return redirect('administracionCatalogo')


def cerrar_sesion(request):
    logout(request)
    return redirect('login')