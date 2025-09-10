# config.py
"""Configuración para el procesamiento de PDFs y generación de corpus."""

import os
from pathlib import Path

# Rutas de archivos y carpetas
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
CORPUS_DIR = BASE_DIR / "corpus"
OUTPUT_DIR = BASE_DIR / "output"

# Configuración de procesamiento
PROCESAMIENTO = {
    "formato_salida": "md",  # "md" o "txt"
    "encoding": "utf-8",
    "longitud_minima_oracion": 10,
    "umbral_deteccion_espanol": 0.2  # 20% de palabras en español para filtrar
}

# Patrones para detectar español (más completos)
PATRONES_ESPANOL = [
    # Artículos y preposiciones comunes
    r'\b(el|la|los|las|un|una|unos|unas)\b',
    r'\b(de|del|en|con|por|para|desde|hasta|entre|sobre|bajo|ante)\b',

    # Pronombres y conjunciones
    r'\b(que|como|cuando|donde|porque|aunque|si|no|sí|pero|sino|y|o|ni)\b',
    r'\b(este|esta|estos|estas|ese|esa|esos|esas|aquel|aquella|aquellos|aquellas)\b',
    r'\b(yo|tú|él|ella|nosotros|nosotras|vosotros|vosotras|ellos|ellas)\b',
    r'\b(me|te|se|le|la|lo|nos|os|les|las|los)\b',

    # Verbos comunes
    r'\b(es|son|está|están|hay|tiene|tienen|ser|estar|tener|hacer|ir|venir)\b',
    r'\b(fue|fueron|era|eran|había|habían|será|serán|estará|estarán)\b',

    # Palabras temporales y espaciales
    r'\b(año|años|día|días|mes|meses|hora|horas|tiempo|momento)\b',
    r'\b(lugar|lugares|aquí|allí|donde|casa|ciudad|país|mundo)\b',

    # Palabras comunes en textos
    r'\b(persona|personas|gente|hombre|mujer|niño|niña|familia)\b',
    r'\b(trabajo|escuela|gobierno|sociedad|cultura|historia)\b',
    r'\b(primero|segundo|tercero|último|mayor|menor|grande|pequeño)\b',

    # Palabras interrogativas
    r'\b(qué|quién|quiénes|cómo|cuándo|cuánto|cuánta|cuántos|cuántas|dónde)\b'
]

# Patrones a ignorar (números de página, referencias, etc.)
PATRONES_IGNORAR = [
    r'^\d+$',  # Solo números
    r'^[IVX]+\.?$',  # Números romanos
    r'^\d+\.\d+\.?\d*$',  # Numeración de secciones
    r'^página\s+\d+$',  # "página X"
    r'^\[\d+\]$',  # Referencias [1]
    r'^fig\.|^figura\s+\d+',  # Referencias a figuras
    r'^tabla\s+\d+',  # Referencias a tablas
    r'^\s*[-*•]\s*$',  # Viñetas solas
]

# Configuración para limpieza de texto
LIMPIEZA_MARKDOWN = {
    "headers": r'#{1,6}\s+',
    "bold": r'\*\*([^*]+)\*\*',
    "italic": r'\*([^*]+)\*',
    "code": r'`([^`]+)`',
    "links": r'\[([^\]]+)\]\([^)]+\)',
    "images": r'!\[([^\]]*)\]\([^)]+\)',
}


# Crear directorios si no existen
def crear_directorios():
    """Crea los directorios necesarios."""
    for directorio in [DATA_DIR, CORPUS_DIR, OUTPUT_DIR]:
        directorio.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    crear_directorios()
    print("✅ Directorios creados")