import requests

# URL de la API
url = "http://192.168.0.7:8000/api/trajes/"

# Datos del traje a enviar
data = {
    "nombre": "Nuevo Traje",
    "region": "La Paz",
    "descripcion": "Traje típico de La Paz con detalles únicos.",
    "talla": "M",
    "genero": "masculino",
    "color_principal": "Rojo",
    "material": "Lana",
    "stock_disponible": 50,
    "modelo_3d_url": "https://storage.googleapis.com/d-trajes-folkloricos.firebasestorage.app/modelos_3d/nuevoTraje.glb"
}

# Archivo de imagen opcional
files = {
    "imagen": open("c:\\Users\\dante\\Desktop\\proyecto_software_trajes\\cuenta\\static\\images\\traje.jpg", "rb")
}

# Enviar datos a la API
response = requests.post(url, data=data, files=files)

# Verificar la respuesta
if response.status_code == 201:
    print("Traje creado exitosamente:", response.json())
else:
    print("Error al crear el traje:", response.status_code, response.text)
