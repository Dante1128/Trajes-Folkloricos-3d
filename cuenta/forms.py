from django import forms
from .models import Alquiler, Garantia, PagoAlquiler, Traje, Usuario

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
    

class TrajeForm(forms.ModelForm):
    modelo_3d = forms.FileField(required=False, label="Archivo Modelo 3D")
    class Meta:
        model = Traje
        fields = [
            'nombre',
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
    monto = forms.DecimalField(max_digits=10, decimal_places=2)
    metodo_pago = forms.ChoiceField(choices=PagoAlquiler.METODO_CHOICES)
    estado_pago = forms.ChoiceField(choices=PagoAlquiler.ESTADO_CHOICES)
    referencia = forms.CharField(max_length=50, required=False)
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

class AlquilarTrajeForm(forms.ModelForm):
    cliente = forms.ModelChoiceField(
        queryset=Usuario.objects.filter(rol='cliente', estado='activo'),
        label="Cliente",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    cantidad = forms.IntegerField(min_value=1, initial=1, label="Cantidad", widget=forms.NumberInput(attrs={'class': 'form-control'}))
    fecha_inicio = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_final = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    estado_garantia = forms.ChoiceField(
        choices=Garantia.ESTADO_CHOICES,
        label="Estado de Garantía",
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    descripcion_garantia = forms.CharField(
        label="Descripción de Garantía",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )

    class Meta:
        model = Alquiler
        fields = [
            'cliente', 'evento', 'fecha_inicio', 'fecha_final', 'cantidad',
            'monto_total', 'metodo_pago', 'estado',
            'estado_garantia', 'descripcion_garantia'
        ]
        widgets = {
            'evento': forms.TextInput(attrs={'class': 'form-control'}),
            'monto_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        fecha_inicio = cleaned_data.get("fecha_inicio")
        fecha_final = cleaned_data.get("fecha_final")
        if fecha_inicio and fecha_final and fecha_final < fecha_inicio:
            raise forms.ValidationError("La fecha final debe ser igual o posterior a la fecha de inicio.")
        return cleaned_data
