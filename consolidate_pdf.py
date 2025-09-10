import os
import shutil
import sys
import string

def consolidar_pdfs(carpeta_entrada):
    # Carpeta de salida
    carpeta_salida = os.path.join(carpeta_entrada, "consolidado")
    os.makedirs(carpeta_salida, exist_ok=True)

    # Iterar sobre las subcarpetas
    for subcarpeta in sorted(os.listdir(carpeta_entrada)):
        ruta_subcarpeta = os.path.join(carpeta_entrada, subcarpeta)

        # Solo procesar carpetas que empiecen con AGR00
        if os.path.isdir(ruta_subcarpeta) and subcarpeta.startswith("AGR"):
            pdfs = [f for f in os.listdir(ruta_subcarpeta) if f.lower().endswith(".pdf")]

            # Ordenar alfabéticamente para consistencia
            pdfs.sort()

            for i, pdf in enumerate(pdfs):
                # Determinar sufijo
                sufijo = "" if len(pdfs) == 1 else f"-{string.ascii_uppercase[i]}"
                nuevo_nombre = f"{subcarpeta}{sufijo}.pdf"

                ruta_origen = os.path.join(ruta_subcarpeta, pdf)
                ruta_destino = os.path.join(carpeta_salida, nuevo_nombre)

                # Copiar el archivo
                shutil.copy2(ruta_origen, ruta_destino)
                print(f"Copiado: {ruta_origen} -> {ruta_destino}")

if __name__ == "__main__":
    carpeta = r"C:\Users\javie\OneDrive\Documentos\PUCP\Tesis 2\extractor\data"
    consolidar_pdfs(carpeta)