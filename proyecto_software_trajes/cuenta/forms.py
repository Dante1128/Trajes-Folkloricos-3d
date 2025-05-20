from django import forms
from .models import Alquiler, Garantia, PagoAlquiler, Traje, Usuario
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


class AlquilerForm(forms.ModelForm):
    class Meta:
        model = Alquiler
        fields = [
            'usuario',
            'traje',
            'evento',
            'fecha_reserva',
            'fecha_inicio',
            'fecha_final',
            'monto_total',
            'metodo_pago',
            'estado',
        ]
        widgets = {
            'fecha_reserva': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'fecha_inicio': forms.DateInput(attrs={'type': 'date'}),
            'fecha_final': forms.DateInput(attrs={'type': 'date'}),
        }

class PagoAlquilerForm(forms.ModelForm):
    class Meta:
        model = PagoAlquiler
        fields = [
            'alquiler',
            'monto',
            'fecha_pago',
            'metodo_pago',
            'estado',
            'referencia',
        ]
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }

class GarantiaForm(forms.ModelForm):
    class Meta:
        model = Garantia
        fields = [
            'alquiler',
            'usuario',
            'estado',
            'descripcion',
        ]
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 3}),
        }