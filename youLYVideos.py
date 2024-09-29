import streamlit as st
import yt_dlp
import json
import os
import subprocess
from datetime import datetime, timedelta

# Título de la aplicación
st.title("Actualizador de Canales de YouTube")

# Definir la ruta del archivo JSON
resultados_path = 'resultado.json'

# Verificar si el archivo de resultados existe
if not os.path.exists(resultados_path):
    st.error("El archivo 'resultado.json' no se encuentra.")
    st.stop()

# Leer el archivo JSON
with open(resultados_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# Mostrar canales disponibles
st.write("Canales disponibles en el archivo:")
for canal in data['Channels']:
    st.write(f"Nombre: {canal['Nombre']} - Fecha de extracción: {canal.get('Fecha de extracción', 'No disponible')}")

# Obtener la fecha límite de 5 días atrás
fecha_limite = datetime.now() - timedelta(days=5)

# Encontrar el primer canal que cumpla con los criterios
canal_seleccionado = None
for canal in data['Channels']:
    fecha_extraccion_str = canal['Fecha de extracción']
    if not fecha_extraccion_str:  # Si no hay fecha de extracción
        canal_seleccionado = canal
        break
    else:
        fecha_extraccion = datetime.strptime(fecha_extraccion_str, '%Y-%m-%d %H:%M:%S')
        if fecha_extraccion < fecha_limite:  # Si la fecha es anterior a los últimos 5 días
            canal_seleccionado = canal
            break

# Verificar si se encontró un canal para actualizar
if canal_seleccionado:
    st.write(f"Canal seleccionado para actualización: {canal_seleccionado['Nombre']}")
else:
    st.warning("No hay canales que necesiten actualización.")
    st.stop()

# Botón para iniciar la extracción de datos
if st.button("Actualizar información del canal"):
    canal_id = canal_seleccionado['CanalID']
    nombre_canal = canal_seleccionado['Nombre']

    # URL del canal
    channel_url = f"https://www.youtube.com/channel/{canal_id}"

    # Configuración para la extracción de información
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # Extrae la lista de videos sin descargar
        'force_generic_extractor': True,
        'skip_download': True,  # No descarga el contenido del video
        'extractor_args': {
            'youtube': {
                'player_client': 'all',  # Usa todos los clientes para la extracción
                'player_skip': 'webpage,js',  # Evita algunas solicitudes de red para robustez
                'skip': 'webpage'  # Omite la descarga de la página inicial
            }
        }
    }

    # Extraer la información del canal
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            result = ydl.extract_info(channel_url, download=False)

            # Guardar la información del canal en un archivo JSON
            os.makedirs('data', exist_ok=True)
            with open(f'data/{nombre_canal}_full_channel_info.json', 'w', encoding='utf-8') as json_file:
                json.dump(result, json_file, ensure_ascii=False, indent=4)

            st.success(f"Información del canal guardada en 'data/{nombre_canal}_full_channel_info.json'.")

            # Actualizar la fecha de extracción en resultados.json
            canal_seleccionado['Fecha de extracción'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # Guardar los cambios en resultados.json
            with open(resultados_path, 'w', encoding='utf-8') as file:
                json.dump(data, file, ensure_ascii=False, indent=4)

            st.success(f"Fecha de extracción actualizada para el canal '{nombre_canal}'.")

            # Ejecutar el script de formateo JSON
            subprocess.run(["python", "formateoJSONYouLY.py", nombre_canal])
            st.success(f"El script de formateo se ha ejecutado para '{nombre_canal}'.")

        except Exception as e:
            st.error(f"Error al extraer información: {e}")

