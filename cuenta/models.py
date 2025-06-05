from django.utils import timezone 
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from rest_framework import serializers




class Usuario(models.Model):
    ROL_CHOICES = [
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]

    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)
    correo = models.EmailField(unique=True)
    celular = models.CharField(max_length=20)
    direccion = models.TextField()
    contrasenia = models.CharField(max_length=128)  # Recomendable usar password hashing
    rol = models.CharField(max_length=10, choices=ROL_CHOICES)
    fecha_registro = models.DateTimeField(default=timezone.now)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='activo')
    
    def __str__(self):
        return f"{self.nombre} {self.apellido}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField()
    imagen = models.ImageField(upload_to='categoria/', null=True, blank=True)

    def __str__(self):
        return self.nombre
    


class Traje(models.Model):
    GENERO_CHOICES = [
        ('masculino', 'Masculino'),
        ('femenino', 'Femenino'),
    ]
    
    nombre = models.CharField(max_length=100)
    categoria = models.ForeignKey('Categoria', on_delete=models.CASCADE)
    region = models.CharField(max_length=100)
    descripcion = models.TextField()
    talla = models.CharField(max_length=20)
    genero = models.CharField(max_length=10, choices=GENERO_CHOICES)
    color_principal = models.CharField(max_length=50)
    material = models.CharField(max_length=100)
    stock_disponible = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='trajes/', null=True, blank=True)  
    modelo_3d_url = models.URLField(null=True, blank=True)
    def __str__(self):
        return f"{self.nombre} - {self.region} ({self.talla})"
        
    class Meta:
        verbose_name = "Traje"
        verbose_name_plural = "Trajes"

class Alquiler(models.Model):
    ESTADO_CHOICES = [
        ('reservado', 'Reservado'),
        ('activo', 'Activo'),
        ('devuelto', 'Devuelto'),
        ('cancelado', 'Cancelado'),
    ]
    
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia Bancaria'),
        ('qr', 'Código QR'),
    ]
    
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE, related_name='alquileres')
    traje = models.ForeignKey('Traje', on_delete=models.CASCADE, related_name='alquileres')
    evento = models.CharField(max_length=255, null=True, blank=True)

    
    fecha_reserva = models.DateTimeField(default=timezone.now)
    fecha_inicio = models.DateField()
    fecha_final = models.DateField()
    
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = models.CharField(max_length=15, choices=METODO_PAGO_CHOICES)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='reservado')
    
    def __str__(self):
        return f"Alquiler #{self.id} - {self.usuario.nombre} - {self.traje.nombre}"
    
    class Meta:
        verbose_name = "Alquiler"
        verbose_name_plural = "Alquileres"
        ordering = ['-fecha_reserva']  # Ordenar por fecha de reserva (más reciente primero)
    
    def dias_alquiler(self):
        """Calcula la duración del alquiler en días"""
        if self.fecha_inicio and self.fecha_final:
            delta = self.fecha_final - self.fecha_inicio
            return delta.days + 1  # +1 porque incluye el primer día
        return 0
    
    def esta_activo(self):
        """Verifica si el alquiler está actualmente activo basado en las fechas"""
        hoy = timezone.now().date()
        return self.fecha_inicio <= hoy <= self.fecha_final and self.estado == 'activo'
    
    def esta_vencido(self):
        """Verifica si el alquiler está vencido (pasó la fecha final pero no ha sido devuelto)"""
        hoy = timezone.now().date()
        return hoy > self.fecha_final and self.estado != 'devuelto' and self.estado != 'cancelado'
    


class Reseña(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    alquiler = models.ForeignKey(Alquiler, on_delete=models.CASCADE)
    calificacion = models.PositiveSmallIntegerField(
         validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comentario = models.TextField()
    fecha_reseña = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"Reseña de {self.usuario.username} sobre {self.alquiler}"
    
class PagoAlquiler(models.Model):
    ESTADO_CHOICES = [
        ('completado', 'Completado'),
        ('pendiente', 'Pendiente'),
        ('cancelado', 'Cancelado'),
    ]

    METODO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('tarjeta', 'Tarjeta'),
        ('transferencia', 'Transferencia'),
        ('qr', 'QR' )
        # Puedes agregar más métodos si los usas
    ]

    alquiler = models.ForeignKey('Alquiler', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateField(default=timezone.now)
    metodo_pago = models.CharField(max_length=20, choices=METODO_CHOICES)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    referencia = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Pago #{self.id} - {self.estado}"
class Garantia(models.Model):
    ESTADO_CHOICES = [
        
        ('devuelto', 'Devuelto'),
        ('no_devuelto', 'No Devuelto'),
    ]

    alquiler = models.ForeignKey('Alquiler', on_delete=models.CASCADE)
    usuario = models.ForeignKey('Usuario', on_delete=models.CASCADE)
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='no_devuelto')
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Garantía de {self.usuario} - {self.estado}"
    


