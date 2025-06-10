from rest_framework import serializers
from .models import Traje, Usuario

class TrajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traje
        fields = [
            'id', 
            'nombre', 
            'region', 
            'descripcion', 
            'talla', 
            'genero', 
            'color_principal', 
            'material', 
            'stock_disponible', 
            'imagen', 
            'modelo_3d_url'
        ]

class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'apellido', 'correo', 'celular', 'rol', 'estado', 'uid']
        extra_kwargs = {
            'celular': {'required': False},  
            'rol': {'read_only': True},
            'estado': {'read_only': True},
        }

