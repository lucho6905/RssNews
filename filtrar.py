import os
import shutil
import difflib

# Lista de palabras o entidades a excluir
exclusiones = ["Enlace:", "Autor:", "Fecha", "Título", "Resumen"]

def eliminar_lineas_repetidas_y_cortas(archivo_entrada, archivo_salida):
    lineas = []
    with open(archivo_entrada, 'r', encoding='utf-8') as archivo:
        try:
            lineas = archivo.readlines()
        except UnicodeDecodeError:
            # Si falla en UTF-8, intenta abrirlo en Latin1
            with open(archivo_entrada, 'r', encoding='latin1') as archivo_latin1:
                lineas = archivo_latin1.readlines()

    # Eliminar líneas duplicadas o muy parecidas, pero excluyendo las palabras o entidades específicas
    lineas_filtradas = []
    for linea in lineas:
        if len(linea.split()) >= 13:  # Filtrar líneas
            es_similar = False
            for linea_filtrada in lineas_filtradas:
                s = difflib.SequenceMatcher(None, linea, linea_filtrada)
                if s.ratio() > 0.5:  # Puedes ajustar este valor según tus necesidades
                    es_similar = True
                    break
            if not es_similar:
                lineas_filtradas.append(linea)
        else:
            # Excluir líneas que contengan palabras o entidades específicas
            for exclusion in exclusiones:
                if exclusion in linea:
                    lineas_filtradas.append(linea)
                    break

    # Guardar las líneas filtradas en el archivo de salida
    with open(archivo_salida, 'w', encoding='utf-8') as archivo:
        archivo.writelines(lineas_filtradas)

def procesar_archivos_en_carpeta(carpeta_entrada, carpeta_salida):
    for raiz, directorios, archivos in os.walk(carpeta_entrada):
        # Crear la estructura de carpetas en la carpeta de salida
        carpeta_relativa = os.path.relpath(raiz, carpeta_entrada)
        carpeta_salida_actual = os.path.join(carpeta_salida, carpeta_relativa)
        os.makedirs(carpeta_salida_actual, exist_ok=True)

        for archivo in archivos:
            if archivo.endswith('.txt'):  # Solo procesar archivos .txt
                archivo_entrada = os.path.join(raiz, archivo)
                archivo_salida = os.path.join(carpeta_salida_actual, archivo)

                # Mensaje de depuración: Mostrar los archivos que se están procesando
                print(f"Procesando archivo: {archivo_entrada} -> {archivo_salida}")

                eliminar_lineas_repetidas_y_cortas(archivo_entrada, archivo_salida)

                # Eliminar el archivo original si el procesamiento fue exitoso
                os.remove(archivo_entrada)

def eliminar_carpetas_vacias(carpeta):
    for raiz, directorios, archivos in os.walk(carpeta, topdown=False):
        for directorio in directorios:
            carpeta_actual = os.path.join(raiz, directorio)
            if not os.listdir(carpeta_actual):
                # Si el directorio está vacío, eliminarlo
                os.rmdir(carpeta_actual)

if __name__ == "__main__":
    carpeta_entrada = "C:/Users/lucho/Downloads/NOTICIAS/Rss"
    carpeta_salida = "C:/Users/lucho/Downloads/NOTICIAS/RssFiltrado"

    if not os.path.exists(carpeta_salida):
        os.makedirs(carpeta_salida)

    # Mensaje de depuración: Mostrar la carpeta de entrada y la carpeta de salida
    print(f"Carpeta de entrada: {carpeta_entrada}")
    print(f"Carpeta de salida: {carpeta_salida}")

    procesar_archivos_en_carpeta(carpeta_entrada, carpeta_salida)

    # Eliminar carpetas vacías en la carpeta de entrada
    eliminar_carpetas_vacias(carpeta_entrada)

