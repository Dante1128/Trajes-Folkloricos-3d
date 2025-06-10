from django.core.management.base import BaseCommand
from django.utils.crypto import get_random_string
from cuenta.models import Usuario

class Command(BaseCommand):
    help = 'Actualizar el campo UID para usuarios existentes'

    def handle(self, *args, **kwargs):
        usuarios = Usuario.objects.filter(uid__isnull=True)
        for usuario in usuarios:
            usuario.uid = get_random_string(32)  # Generar un UID único
            usuario.save()
        self.stdout.write(self.style.SUCCESS('UID actualizado para todos los usuarios existentes.'))
