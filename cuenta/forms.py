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
    modelo_3d = forms.FileField(required=False, label="Archivo Modelo 3D")
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
             'imagen',
             'modelo_3d_url',
        ]



class ReservaCompletaForm(forms.Form):
    usuario = forms.ModelChoiceField(queryset=Usuario.objects.all())
    traje = forms.ModelChoiceField(queryset=Traje.objects.all())
    evento = forms.CharField(max_length=100)
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_final = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
   

    estado = forms.ChoiceField(choices=Alquiler.ESTADO_CHOICES)
    # Campos de pago
    monto = forms.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = forms.ChoiceField(choices=PagoAlquiler.METODO_CHOICES)
    estado_pago = forms.ChoiceField(choices=PagoAlquiler.ESTADO_CHOICES)
    referencia = forms.CharField(max_length=50, required=False)
    
    # Campos de garantía
    estado_garantia = forms.ChoiceField(choices=Garantia.ESTADO_CHOICES)
    descripcion_garantia = forms.CharField(widget=forms.Textarea, required=False)

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_final = cleaned_data.get("fecha_final")
        monto = cleaned_data.get("monto")

        if fecha_inicio and fecha_final and fecha_final < fecha_inicio:
            raise forms.ValidationError("La fecha final debe ser igual o posterior a la fecha de inicio.")

        if monto is not None and monto <= 0:
            raise forms.ValidationError("El monto debe ser mayor a cero.")
