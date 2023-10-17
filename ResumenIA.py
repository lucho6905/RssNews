import os
import re
from transformers import BartForConditionalGeneration, BartTokenizer
from langdetect import detect
import traceback


# Función para leer archivos de texto en un directorio
def read_text_files_in_directory(directory):
    news_text = []
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".txt"):
                with open(os.path.join(root, file), "r", encoding="utf-8") as f:
                    news_text.append((root, file, f.read()))  # Guarda la ruta, nombre del archivo y su contenido
    return news_text


# Directorio que contiene los archivos de noticias
news_directory = "C:/Users/lucho/Downloads/NOTICIAS/RssFiltrado"

# Lee las noticias
news_data = read_text_files_in_directory(news_directory)

# Inicializa el modelo BART y el tokenizador para español
model_name = "facebook/bart-large-cnn"
model = BartForConditionalGeneration.from_pretrained(model_name)
tokenizer = BartTokenizer.from_pretrained("facebook/bart-large-cnn", src_lang="es", tgt_lang="es")

# Expresiones regulares para extraer las entidades
titulo_pattern = re.compile(r'Título: (.+)')
enlace_pattern = re.compile(r'Enlace: (.+)')
autor_pattern = re.compile(r'Autor: (.+)')
fecha_pattern = re.compile(r'Fecha: (.+)')
resumen_pattern = re.compile(r'Resumen: (.+)')  # Add a pattern for extracting the "Resumen" section

# Directorio donde se guardarán los resúmenes manteniendo la estructura original
output_base_directory = "C:/Users/lucho/Downloads/NOTICIAS/NoticiasResumidas"

# Genera resúmenes y guarda en archivos de texto
for root, file_name, news_text in news_data:
    print("Procesando:", file_name)

    # Detecta el idioma del texto utilizando langdetect
    try:
        detected_language = detect(news_text)
        if detected_language == "es":
            # Configura el modelo y el tokenizador para español
            model.config.tgt_lang = "es"
            tokenizer.src_lang = "es"
            tokenizer.tgt_lang = "es"
        elif detected_language == "en":
            # Configura el modelo y el tokenizador para inglés
            model.config.tgt_lang = "en"
            tokenizer.src_lang = "en"
            tokenizer.tgt_lang = "en"
        elif detected_language == "gl":
            # Configura el modelo y el tokenizador para gallego
            model.config.tgt_lang = "gl"
            tokenizer.src_lang = "gl"
            tokenizer.tgt_lang = "gl"
    except Exception as e:
        traceback.print_exc()
        # Establece un valor predeterminado en caso de error
        model.config.tgt_lang = "es"
        tokenizer.src_lang = "es"
        tokenizer.tgt_lang = "es"

    # Preprocesa el texto
    preprocessed_text = news_text

    # Utiliza expresiones regulares para extraer entidades
    titulo_match = titulo_pattern.search(preprocessed_text)
    enlace_match = enlace_pattern.search(preprocessed_text)
    autor_match = autor_pattern.search(preprocessed_text)
    fecha_match = fecha_pattern.search(preprocessed_text)
    resumen_match = resumen_pattern.search(preprocessed_text)  # Find the "Resumen" section

    titulo = titulo_match.group(1) if titulo_match else "Título no encontrado"
    enlace = enlace_match.group(1) if enlace_match else "Enlace no encontrado"
    autor = autor_match.group(1) if autor_match else "Autor no encontrado"
    fecha = fecha_match.group(1) if fecha_match else "Fecha no encontrada"

    # Extract the "Resumen" section
    resumen_text = resumen_match.group(1) if resumen_match else "Resumen no encontrado"

    # Generate the summary for the "Resumen" section
    inputs = tokenizer.encode(resumen_text, return_tensors="pt", truncation=True)
    summary_ids = model.generate(inputs, max_new_tokens=1024, min_new_tokens=512, length_penalty=1.3, num_beams=2,
                                 early_stopping=True)
    summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

    # Combine the summary generated with the entities
    final_summary = f"Título: {titulo}\nResumen: {summary}\nEnlace: {enlace}\nAutor: {autor}\nFecha: {fecha}"

    # Create the output path based on the original directory structure
    relative_path = os.path.relpath(root, news_directory)  # Ruta relativa desde el directorio de noticias
    output_subdirectory = os.path.join(output_base_directory, relative_path)
    os.makedirs(output_subdirectory, exist_ok=True)  # Crea la estructura de directorios si no existe

    # Guarda el resumen en un archivo de texto en la estructura de directorios correspondiente
    output_file_path = os.path.join(output_subdirectory, f"{file_name}_summary.txt")
    with open(output_file_path, "w", encoding="utf-8") as output_file:
        output_file.write(final_summary)

    print(f"Resumen guardado en:", output_file_path)  # Mensaje de depuración

print("Resúmenes generados y guardados en archivos de texto en", output_base_directory)
