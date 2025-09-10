#!/usr/bin/env python3
"""
Script principal para extraer texto de PDFs y generar corpus monolingües en awajún.
Uso: python main.py [carpeta_pdfs] [archivo_corpus_salida]
"""

import sys
import argparse
from pathlib import Path

# Importar nuestras clases
from pdf_extractor import PDFExtractor, CorpusGenerator
from config import crear_directorios, DATA_DIR, CORPUS_DIR


def procesar_argumentos():
    """Procesa los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description="Extrae texto de PDFs y genera corpus monolingües en awajún"
    )

    parser.add_argument(
        "carpeta_pdfs",
        nargs="?",
        default="./data",
        help="Carpeta que contiene los archivos PDF (default: ./data)"
    )

    parser.add_argument(
        "archivo_corpus",
        nargs="?",
        default="./corpus/awajun_corpus.txt",
        help="Archivo de salida del corpus (default: ./corpus/awajun_corpus.txt)"
    )

    parser.add_argument(
        "--solo-extraccion",
        action="store_true",
        help="Solo extraer texto de PDFs, no generar corpus"
    )

    parser.add_argument(
        "--solo-corpus",
        action="store_true",
        help="Solo generar corpus de archivos ya procesados"
    )

    parser.add_argument(
        "--formato",
        choices=["md", "txt"],
        default="md",
        help="Formato de salida para extracción (default: md)"
    )

    return parser.parse_args()


def main():
    """Función principal."""
    # Crear directorios necesarios
    crear_directorios()

    # Procesar argumentos
    args = procesar_argumentos()

    # Mostrar configuración
    print("🔧 Configuración:")
    print(f"   Carpeta PDFs: {args.carpeta_pdfs}")
    print(f"   Archivo corpus: {args.archivo_corpus}")
    print(f"   Formato: {args.formato}")
    print()

    # Verificar que la carpeta existe
    carpeta_path = Path(args.carpeta_pdfs)
    if not carpeta_path.exists():
        print(f"❌ Error: La carpeta {args.carpeta_pdfs} no existe")
        sys.exit(1)

    try:
        if not args.solo_corpus:
            # 1. Extraer texto de PDFs a carpeta output
            print("🔄 Extrayendo texto de PDFs con docling...")
            extractor = PDFExtractor()
            extractor.procesar_pdfs(args.carpeta_pdfs, args.formato)
            print("✅ Extracción completada\n")

        if not args.solo_extraccion:
            # 2. Generar corpus monolingüe desde carpeta output
            print("🔄 Generando corpus monolingüe en awajún...")
            generador = CorpusGenerator()
            generador.generar_corpus_monolingue("./output", args.archivo_corpus)
            print("✅ Corpus generado exitosamente")

    except KeyboardInterrupt:
        print("\n⚠️ Proceso interrumpido por el usuario")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()