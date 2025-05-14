from django import forms
from .models import Traje, Usuario
from .models import Categoria

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'apellido', 'correo', 'celular', 'direccion', 'estado'] 

    def clean_nombre(self):
        nombre = self.cleaned_data.get('nombre')
        if len(nombre) < 3:
            raise forms.ValidationError("El nombre debe tener al menos 3 caracteres.")
        return nombre

    def clean_celular(self):
        celular = self.cleaned_data.get('celular')
        if not celular.isdigit() or len(celular) != 7:
            raise forms.ValidationError("El celular debe tener 7 dígitos numéricos.")
        return celular

    def save(self, commit=True):
        
        usuario = super().save(commit=False)
        if commit:
            usuario.rol = 'cliente' 
            usuario.save()
        return usuario
    

class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control'}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),

        }

class TrajeForm(forms.ModelForm):
    class Meta:
        model = Traje
        fields = [
            'nombre',
            'categoria',
            'region',
            'descripcion',
            'talla',
            'genero',
            'color_principal',
            'material',
            'stock_disponible',
        ]
