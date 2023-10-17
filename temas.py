import os
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import re
import shutil
import torch

# Cargar el modelo "website_classification"
model_checkpoint = "alimazhar-110/website_classification"
tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
model = AutoModelForSequenceClassification.from_pretrained(model_checkpoint)

# Directorio raíz donde se encuentran tus archivos de texto
root_directory = "C:/Users/lucho/OneDrive/Documentos/Descargas/IALab"

# Definir las categorías y sus puntuaciones correspondientes
categorias = {
    "Social Networking and Messaging": 0.407,
    "Adult": 0.083,
    "Photography": 0.082,
    "E-Commerce": 0.063,
    "Streaming Services": 0.058,
    "Computers and Technology": 0.042,
    "Health and Fitness": 0.035,
    "Sports": 0.034,
    "Food": 0.030,
    "News": 0.030,
    "Law and Government": 0.027,
    "Games": 0.026,
    "Business/Corporate": 0.024,
    "Travel": 0.021,
    "Education": 0.020,
    "Forums": 0.017
}

# Directorio de salida para cada categoría
output_directories = {categoria: f"C:/Users/lucho/OneDrive/Documentos/Descargas/Cat/{categoria.replace(' ', '_')}" for categoria in categorias}

def obtener_texto_enlace(archivo):
    print(f"Obteniendo texto del enlace del archivo: {archivo}")
    # Leer el contenido del archivo de texto
    with open(archivo, "r", encoding="utf-8") as file:
        contenido = file.read()

    # Buscar el texto del enlace
    pattern = r'Enlace:\s*(.*?)\n'
    match = re.search(pattern, contenido)
    if match:
        texto_enlace = match.group(1)
    else:
        texto_enlace = ""

    # Imprimir el texto del enlace
    print(f"Texto del enlace: {texto_enlace}")

    return texto_enlace

def verificar_archivo(archivo):
    print(f"Verificando archivo: {archivo}")
    # Obtener el texto del enlace
    texto_enlace = obtener_texto_enlace(archivo)

    # Tokenizar el texto y clasificarlo
    inputs = tokenizer(texto_enlace, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    probabilities = logits.softmax(dim=1)
    predicted_class = probabilities.argmax(dim=1).item()
    predicted_category = list(categorias.keys())[predicted_class]
    confidence_score = probabilities[0][predicted_class].item()

    # Devolver el resultado de la clasificación
    return predicted_category, confidence_score

def verificar_archivos_en_directorio(directorio):
    # Recorrer los archivos en el directorio actual
    for raiz, carpetas, archivos in os.walk(directorio):
        for archivo in archivos:
            if archivo.endswith(".txt"):
                # Obtener la ruta completa del archivo original
                ruta_completa = os.path.join(raiz, archivo)

                # Obtener la ruta relativa del archivo con respecto al directorio raíz
                ruta_relativa = os.path.relpath(ruta_completa, root_directory)

                # Obtener la categoría predicha para el archivo
                categoria_predicha, confianza = verificar_archivo(ruta_completa)

                # Obtener la carpeta de salida correspondiente para la categoría predicha
                carpeta_salida = output_directories[categoria_predicha]

                # Crear la estructura de carpetas en el destino si no existe
                os.makedirs(os.path.join(carpeta_salida, os.path.dirname(ruta_relativa)), exist_ok=True)

                # Construir la ruta de destino conservando la estructura de carpetas original
                destino = os.path.join(carpeta_salida, ruta_relativa)

                # Mover el archivo a la carpeta correspondiente
                shutil.move(ruta_completa, destino)

    # Recorrer los archivos en el directorio actual
    for raiz, carpetas, archivos in os.walk(directorio):
        for archivo in archivos:
            if archivo.endswith(".txt"):
                # Obtener la ruta completa del archivo original
                ruta_completa = os.path.join(raiz, archivo)

                # Clasificar el archivo según el modelo
                categoria_predicha, confianza = verificar_archivo(ruta_completa)

                # Mover el archivo a la carpeta correspondiente
                destino = os.path.join(output_directories[categoria_predicha], archivo)
                shutil.move(ruta_completa, destino)

def eliminar_carpetas_vacias(directorio):
    # Recorrer el directorio en orden inverso para asegurarse de eliminar carpetas anidadas primero
    for raiz, carpetas, archivos in os.walk(directorio, topdown=False):
        for carpeta in carpetas:
            carpeta_completa = os.path.join(raiz, carpeta)
            # Verificar si la carpeta está vacía
            if not os.listdir(carpeta_completa):
                print(f"Eliminando carpeta vacía: {carpeta_completa}")
                os.rmdir(carpeta_completa)

if __name__ == "__main__":
    print(f"Directorio raíz: {root_directory}")
    verificar_archivos_en_directorio(root_directory)

    for categoria, output_directory in output_directories.items():
        print(f"Archivos de '{categoria}' movidos a {output_directory}")

    # Eliminar carpetas vacías en el directorio de entrada
    eliminar_carpetas_vacias(root_directory)
