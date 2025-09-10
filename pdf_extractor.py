import os
import re
from pathlib import Path
from typing import List, Optional
from docling.document_converter import DocumentConverter
from langdetect import detect, DetectorFactory, LangDetectException

# Para resultados consistentes en langdetect
DetectorFactory.seed = 0


class PDFExtractor:
    """Clase para extraer texto de PDFs usando docling."""

    def __init__(self):
        self.converter = DocumentConverter()

    def extraer_texto_pdf(self, ruta_pdf: str) -> str:
        """Extrae texto de un PDF usando docling."""
        try:
            result = self.converter.convert(ruta_pdf)
            doc = result.document
            return doc.export_to_markdown()
        except Exception as e:
            print(f"❌ Error al procesar {ruta_pdf}: {e}")
            return ""

    def procesar_pdfs(self, carpeta_origen: str, carpeta_destino: Optional[str] = None,
                      formato_salida: str = "md") -> None:
        """Procesa todos los PDFs de una carpeta y guarda el resultado en carpeta destino."""
        carpeta_origen_path = Path(carpeta_origen)

        # Si no se especifica carpeta destino, usar la misma carpeta origen
        if carpeta_destino is None:
            carpeta_destino_path = carpeta_origen_path
        else:
            carpeta_destino_path = Path(carpeta_destino)
            # Crear la carpeta destino si no existe
            carpeta_destino_path.mkdir(parents=True, exist_ok=True)

        if not carpeta_origen_path.exists():
            print(f"❌ La carpeta {carpeta_origen} no existe")
            return

        archivos_pdf = list(carpeta_origen_path.glob("*.pdf"))

        if not archivos_pdf:
            print(f"⚠️ No se encontraron archivos PDF en {carpeta_origen}")
            return

        for ruta_pdf in archivos_pdf:
            contenido = self.extraer_texto_pdf(str(ruta_pdf))

            if contenido:
                extension = ".md" if formato_salida == "md" else ".txt"
                nombre_out = ruta_pdf.stem + extension
                # Guardar en la carpeta destino
                ruta_out = carpeta_destino_path / nombre_out

                with open(ruta_out, "w", encoding="utf-8") as f:
                    f.write(contenido)

                print(f"✅ Procesado: {ruta_pdf.name} → {carpeta_destino_path / nombre_out}")


class CorpusGenerator:
    """Clase para generar corpus monolingües en Awajún."""

    def __init__(self):
        # Patrones de ruido técnico para eliminar
        self.patrones_ruido = [
            r'<!-- image -->',  # Marcadores de imagen
            r'^\d+$',  # Solo números
            r'^[IVX]+\.$',  # Numeración romana
            r'^#{1,6}\s+$',  # Headers vacíos
            r'^\s*-+\s*$',  # Líneas de guiones
            r'^\s*=+\s*$',  # Líneas de igual
            r'^\s*\*+\s*$',  # Líneas de asteriscos
        ]

        # Palabras/frases que indican contenido administrativo en español
        self.indicadores_administrativo = [
            'evaluación', 'resultados', 'estimado', 'padre', 'madre', 'familia',
            'ministerio', 'universidad', 'departamento', 'región', 'provincia',
            'nivel', 'grado', 'año', 'fecha', 'página', 'índice', 'capítulo',
            'anexo', 'bibliografía', 'referencias', 'tabla', 'gráfico',
            'pregunta', 'respuesta', 'instrucción', 'procedimiento'
        ]

    def es_ruido_tecnico(self, texto: str) -> bool:
        """Detecta si una línea es ruido técnico."""
        for patron in self.patrones_ruido:
            if re.match(patron, texto.strip(), re.IGNORECASE):
                return True
        return False

    def es_administrativo(self, texto: str) -> bool:
        """Detecta si contiene términos administrativos típicos en español."""
        texto_lower = texto.lower()
        for indicador in self.indicadores_administrativo:
            if indicador in texto_lower:
                return True
        return False

    def detectar_idioma(self, texto: str) -> str:
        """Detecta el idioma del texto usando langdetect."""
        try:
            # Mínimo 10 caracteres para detección confiable
            if len(texto.strip()) < 10:
                return "unknown"

            idioma = detect(texto)
            return idioma
        except LangDetectException:
            return "unknown"

    def es_probablemente_espanol(self, texto: str) -> bool:
        """
        Determina si el texto es español usando múltiples estrategias.
        Prioriza conservar awajún en caso de duda.
        """
        # Filtros rápidos primero
        if self.es_ruido_tecnico(texto):
            return True

        if self.es_administrativo(texto):
            return True

        # Detección de idioma
        idioma = self.detectar_idioma(texto)

        # Si detecta español claramente, eliminar
        if idioma == "es":
            return True

        # Si detecta otros idiomas conocidos (inglés, francés, etc.), también eliminar
        if idioma in ["en", "fr", "it", "pt", "de"]:
            return True

        # Si no puede detectar o detecta algo desconocido, CONSERVAR (podría ser awajún)
        return False

    def limpiar_texto(self, texto: str) -> str:
        """Limpia el texto eliminando formato markdown y normalizando."""
        # Remover patrones de markdown y formato
        texto = re.sub(r'#{1,6}\s+', '', texto)  # Headers
        texto = re.sub(r'\*\*([^*]+)\*\*', r'\1', texto)  # Bold
        texto = re.sub(r'\*([^*]+)\*', r'\1', texto)  # Italic
        texto = re.sub(r'`([^`]+)`', r'\1', texto)  # Code
        texto = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', texto)  # Links
        texto = re.sub(r'<!-- image -->', '', texto)  # Marcadores de imagen

        # Limpiar espacios múltiples y saltos de línea
        texto = re.sub(r'\n+', '\n', texto)
        texto = re.sub(r'[ \t]+', ' ', texto)

        return texto.strip()

    def limpiar_oracion(self, oracion: str) -> str:
        """
        Limpia una oración individual aplicando reglas específicas para awajún.
        """
        oracion = oracion.strip()

        # A) Eliminar guiones al inicio de línea (items de lista)
        oracion = re.sub(r'^-\s+', '', oracion)

        # B) Eliminar números/referencias al final de oraciones (. 4, : 8, etc.)
        oracion = re.sub(r'[.:]?\s*\d+\s*$', '', oracion)

        # NUEVA REGLA: Eliminar puntos suspensivos y números de índice
        # Ejemplo: "Yusa ................................. 6" -> "Yusa"
        oracion = re.sub(r'\.{3,}.*?\d+\s*$', '', oracion)
        oracion = re.sub(r'\.{3,}', '', oracion)  # Eliminar puntos suspensivos restantes

        # C & D) Procesar contenido de tablas
        if '|' in oracion:
            # Eliminar filas de separación de tablas (solo guiones y pipes)
            if re.match(r'^[\s\|\-]+$', oracion):
                return ""

            # Dividir por pipes y procesar cada celda
            celdas = oracion.split('|')
            celdas_limpias = []

            for celda in celdas:
                celda = celda.strip()
                # Saltar celdas vacías o que solo tienen guiones
                if not celda or re.match(r'^[\-\s]+$', celda):
                    continue

                # Saltar celdas que son solo números (números de página/índice)
                if re.match(r'^\d+$', celda):
                    continue

                # Limpiar puntos suspensivos y números en la celda
                celda = re.sub(r'\.{3,}.*?\d+\s*$', '', celda)
                celda = re.sub(r'\.{3,}', '', celda)
                celda = celda.strip()

                # Procesar múltiples oraciones en una celda (separadas por •)
                if '•' in celda:
                    sub_oraciones = celda.split('•')
                    for sub_oracion in sub_oraciones:
                        sub_oracion = sub_oracion.strip()
                        if sub_oracion and len(sub_oracion) > 3:
                            celdas_limpias.append(sub_oracion)
                else:
                    if len(celda) > 3:
                        celdas_limpias.append(celda)

            # Si encontramos celdas válidas, retornar la primera válida
            # (las otras se procesarán por separado)
            if celdas_limpias:
                return celdas_limpias[0]
            else:
                return ""

        # D) Procesar oraciones que empiezan con •
        if oracion.startswith('•'):
            oracion = oracion[1:].strip()

        # E) Eliminar comas al inicio de oración
        oracion = re.sub(r'^,\s+', '', oracion)

        # Limpiar espacios extra
        oracion = re.sub(r'\s+', ' ', oracion).strip()

        return oracion

    def procesar_tablas(self, texto: str) -> List[str]:
        """
        Extrae todas las celdas válidas de tablas en el texto.
        """
        oraciones_tabla = []
        lineas = texto.split('\n')

        for linea in lineas:
            if '|' in linea:
                # Saltar filas de separación
                if re.match(r'^[\s\|\-]+$', linea):
                    continue

                celdas = linea.split('|')
                for celda in celdas:
                    celda = celda.strip()
                    if not celda or re.match(r'^[\-\s]+$', celda):
                        continue

                    # Saltar celdas que son solo números
                    if re.match(r'^\d+$', celda):
                        continue

                    # Limpiar puntos suspensivos y números
                    celda = re.sub(r'\.{3,}.*?\d+\s*$', '', celda)
                    celda = re.sub(r'\.{3,}', '', celda)
                    celda = celda.strip()

                    if not celda or len(celda) <= 3:
                        continue

                    # Procesar múltiples oraciones en celda (separadas por •)
                    if '•' in celda:
                        sub_oraciones = celda.split('•')
                        for sub_oracion in sub_oraciones:
                            sub_oracion_limpia = self.limpiar_oracion(sub_oracion)
                            if sub_oracion_limpia and len(sub_oracion_limpia) > 3:
                                oraciones_tabla.append(sub_oracion_limpia)
                    else:
                        celda_limpia = self.limpiar_oracion(celda)
                        if celda_limpia and len(celda_limpia) > 3:
                            oraciones_tabla.append(celda_limpia)

        return oraciones_tabla

    def segmentar_oraciones(self, texto: str) -> List[str]:
        """
        Segmenta el texto en oraciones, adaptado para awajún.
        Más conservador para preservar texto de lengua de bajos recursos.
        """
        oraciones = []

        # Primero extraer oraciones de tablas
        oraciones_tabla = self.procesar_tablas(texto)
        oraciones.extend(oraciones_tabla)

        # Luego procesar líneas normales (excluyendo las que tienen tablas)
        lineas = texto.split('\n')

        for linea in lineas:
            # Saltar líneas que contienen tablas (ya procesadas)
            if '|' in linea:
                continue

            linea = linea.strip()

            # Saltar líneas muy cortas o vacías
            if len(linea) < 3:
                continue

            # Procesar oraciones con • (items de lista)
            if '•' in linea:
                items = linea.split('•')
                for item in items:
                    item_limpio = self.limpiar_oracion(item)
                    if item_limpio and len(item_limpio) >= 3:
                        oraciones.append(item_limpio)
                continue

            # Si la línea no tiene puntuación final, probablemente es una oración completa
            if not re.search(r'[.!?;:]$', linea):
                linea_limpia = self.limpiar_oracion(linea)
                if linea_limpia and len(linea_limpia) >= 3:
                    oraciones.append(linea_limpia)
            else:
                # Dividir por puntuación, pero conservadoramente
                sub_oraciones = re.split(r'[.!?]+', linea)
                for sub_oracion in sub_oraciones:
                    sub_oracion_limpia = self.limpiar_oracion(sub_oracion)
                    if sub_oracion_limpia and len(sub_oracion_limpia) >= 3:
                        oraciones.append(sub_oracion_limpia)

        return oraciones

    def extraer_oraciones_awajun(self, archivo_texto: str) -> List[str]:
        """Extrae oraciones en awajún de un archivo de texto."""
        try:
            with open(archivo_texto, 'r', encoding='utf-8') as f:
                contenido = f.read()
        except Exception as e:
            print(f"❌ Error al leer {archivo_texto}: {e}")
            return []

        # Limpiar el texto
        contenido = self.limpiar_texto(contenido)

        # Segmentar en oraciones
        oraciones_candidatas = self.segmentar_oraciones(contenido)

        # Filtrar por idioma
        oraciones_awajun = []
        for oracion in oraciones_candidatas:
            if not self.es_probablemente_espanol(oracion):
                oraciones_awajun.append(oracion)

        return oraciones_awajun

    def generar_corpus_monolingue(self, carpeta_origen: str, carpeta_corpus: str) -> None:
        """
        Genera archivos individuales y un corpus consolidado con oraciones awajún.
        """
        carpeta_origen_path = Path(carpeta_origen)
        carpeta_corpus_path = Path(carpeta_corpus)

        if not carpeta_origen_path.exists():
            print(f"❌ La carpeta {carpeta_origen} no existe")
            return

        # Crear carpeta corpus
        carpeta_corpus_path.mkdir(parents=True, exist_ok=True)

        # Buscar archivos de texto procesados
        archivos_texto = list(carpeta_origen_path.glob("*.md")) + list(carpeta_origen_path.glob("*.txt"))

        if not archivos_texto:
            print(f"⚠️ No se encontraron archivos de texto en {carpeta_origen}")
            return

        todas_oraciones = []
        estadisticas_por_archivo = {}

        print(f"\n🔄 Procesando archivos para extraer awajún...")

        for archivo in archivos_texto:
            print(f"📖 Procesando: {archivo.name}")
            oraciones = self.extraer_oraciones_awajun(str(archivo))

            if oraciones:
                # Guardar archivo individual
                nombre_awajun = archivo.stem + "_awajun.txt"
                ruta_awajun = carpeta_corpus_path / nombre_awajun

                with open(ruta_awajun, 'w', encoding='utf-8') as f:
                    for oracion in oraciones:
                        f.write(oracion + '\n')

                todas_oraciones.extend(oraciones)
                estadisticas_por_archivo[archivo.name] = len(oraciones)
                print(f"   ✅ {len(oraciones)} oraciones extraídas → {nombre_awajun}")
            else:
                estadisticas_por_archivo[archivo.name] = 0
                print(f"   ⚠️ No se encontraron oraciones awajún válidas")

        # Remover duplicados manteniendo el orden
        oraciones_unicas = list(dict.fromkeys(todas_oraciones))

        # Guardar corpus consolidado
        corpus_consolidado = carpeta_corpus_path / "awajun_corpus_completo.txt"
        with open(corpus_consolidado, 'w', encoding='utf-8') as f:
            for oracion in oraciones_unicas:
                f.write(oracion + '\n')

        # Mostrar estadísticas
        print(f"\n📊 ESTADÍSTICAS FINALES:")
        print(f"{'=' * 50}")
        print(f"Archivos procesados: {len(archivos_texto)}")
        print(f"\nOraciones por archivo:")
        for archivo, count in estadisticas_por_archivo.items():
            print(f"  • {archivo}: {count} oraciones")
        print(f"\nTotales:")
        print(f"  • Oraciones extraídas: {len(todas_oraciones)}")
        print(f"  • Oraciones únicas: {len(oraciones_unicas)}")
        print(f"  • Corpus consolidado: {corpus_consolidado}")
        print(f"  • Archivos individuales: {carpeta_corpus_path}")
        print(f"{'=' * 50}")


def main():
    """Función principal."""
    # Configuración
    carpeta_pdfs = "./data"
    carpeta_output = "./output"
    carpeta_corpus = "./corpus"

    # 1. Extraer texto de PDFs a carpeta output
    print("🔄 Extrayendo texto de PDFs a carpeta output...")
    #extractor = PDFExtractor()
    #extractor.procesar_pdfs(carpeta_pdfs, carpeta_output)

    # 2. Generar corpus monolingüe awajún
    print("\n🔄 Generando corpus monolingüe awajún...")
    generador = CorpusGenerator()
    generador.generar_corpus_monolingue(carpeta_output, carpeta_corpus)

    print(f"\n🎉 ¡Proceso completado! Revisa la carpeta {carpeta_corpus}")

if __name__ == '__main__':
    main()