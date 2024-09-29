import sys
import json
import os

# Asegúrate de que se pase el argumento nombre_canal
if len(sys.argv) < 2:
    print("Por favor, proporciona el nombre del canal como argumento.")
    sys.exit(1)

nombre_canal = sys.argv[1]

# Nombre del archivo JSON que contiene toda la información del canal
input_json_file = f'data/{nombre_canal}_full_channel_info.json'
# Nombre del archivo JSON donde se guardará la información extraída
output_json_file = f'data/{nombre_canal}_extracted_video_info.json'

# Cargar el JSON desde el archivo
with open(input_json_file, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Lista para almacenar la información de los videos extraída
extracted_video_info = []

def extract_video_info(entries, id_counter, channel_name):
    for entry in entries:
        if '_type' in entry and entry['_type'] == 'url':
            video_info = {
                'id_num': id_counter[0],  # Asigna el número de ID actual
                'id': entry.get('id'),
                'title': entry.get('title'),
                'channel': channel_name  # Usar el nombre del canal proporcionado
            }
            extracted_video_info.append(video_info)
            id_counter[0] += 1  # Incrementa el contador después de añadir un video
        elif 'entries' in entry:
            # Llamar recursivamente para buscar en subniveles
            extract_video_info(entry['entries'], id_counter, channel_name)

# Extraer el nombre del canal de la raíz
channel_name = data.get('channel', 'Unknown Channel')

# Comenzar la extracción desde el primer nivel de entries
id_counter = [1]  # Usamos una lista para mantener la referencia en las llamadas recursivas
if 'entries' in data:
    extract_video_info(data['entries'], id_counter, channel_name)

# Guardar la información extraída en un nuevo archivo JSON
with open(output_json_file, 'w', encoding='utf-8') as file:
    json.dump(extracted_video_info, file, indent=4, ensure_ascii=False)

print(f"Información extraída guardada en '{output_json_file}'.")

# Eliminar el archivo JSON de entrada
if os.path.exists(input_json_file):
    os.remove(input_json_file)
    print(f"Archivo '{input_json_file}' eliminado.")
else:
    print(f"El archivo '{input_json_file}' no existe.")

