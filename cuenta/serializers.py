from rest_framework import serializers
from .models import Categoria
from .models import Traje

class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ['id', 'nombre', 'descripcion', 'imagen']



class TrajeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Traje
        fields = '__all__'
